from itertools import combinations
from typing import Dict, List, Optional, Set, TextIO, Tuple, Union

from eis1600.gazetteers.Toponyms import Toponyms, YAMLToponym
from eis1600.helper.markdown_methods import get_yrs_tag_value
from eis1600.helper.EntityTags import EntityTags
from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.miu.YAMLHandler import YAMLHandler
from eis1600.helper.markdown_patterns import ENTITY_TAGS_PATTERN, MIU_HEADER_PATTERN, NEWLINES_CROWD_PATTERN


def create_yml_header(category: str, headings: Optional[HeadingTracker] = None) -> str:
    """Creates a YAML header for the current MIU file and returns it as yamlfied string.

    :param str category: Category of the entry.
    :param Type[HeadingsTracker] headings: HeadingTracker with the super elements of the current MIU, optional.
    :return str: YAML header for the current MIU.
    """
    yml_header = YAMLHandler()
    yml_header.set_category(category)
    if headings:
        yml_header.set_headings(headings)

    return yml_header.get_yamlfied()


def extract_yml_header_and_text(miu_file_object: TextIO, is_header: Optional[bool] = False) -> (str, str):
    """ Returns the YAML header and the text as a tuple from MIU file object.

    Splits the MIU file into a tuple of YAML header and text.
    :param TextIO miu_file_object: File object of the MIU file from which to extract YAML header and text.
    :param bool is_header: Indicates if the current MIU is the YAML header of the whole work and if so skips
    removing
    blank lines, defaults to False.
    :return (str, str): Tuple of the extracted YAML header and text.
    """
    text = ''
    miu_yml_header = ''
    for line in iter(miu_file_object):
        if MIU_HEADER_PATTERN.match(line):
            # Omit the #MIU#Header# line as it is only needed inside the MIU.EIS1600 file, but not in YMLDATA.yml
            next(miu_file_object)
            line = next(miu_file_object)
            miu_yml_header = ''
            while not MIU_HEADER_PATTERN.match(line):
                miu_yml_header += line
                line = next(miu_file_object)
            # Omit the empty line between the header content and the #MIU#Header# line
            miu_yml_header = miu_yml_header[:-2]
            # Skip empty line after #MIU#Header#
            next(miu_file_object)
        else:
            text += line
        # Replace new lines which separate YAML header from text
        if not is_header:
            text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)

    return miu_yml_header, text


def add_to_entities_dict(
        entities_dict: Dict, cat: str,
        entity: Union[str, Tuple[str, Union[int, str]], List[Tuple[str, str]], List[str], Tuple[int, str], Dict],
        tag: Optional[str] = None
) -> None:
    """Add a tagged entity to the respective list in the entities_dict.

    :param Dict entities_dict: Dict containing previous tagged entities.
    :param str cat: Category of the entity.
    :param Union[str|int] entity: Entity - might be int if entity is a date, otherwise str.
    :param str tag: Onomastic classification, used to differentiate between onomastic elements, optional.
    """
    cat = cat.lower() + 's'
    if tag:
        tag = tag.lower()
    if cat in entities_dict.keys():
        if cat == 'onomastics' and tag:
            if tag in entities_dict[cat].keys():
                entities_dict[cat][tag].append(entity)
            else:
                entities_dict[cat][tag] = [entity]
        else:
            entities_dict[cat].append(entity)
    else:
        if cat == 'onomastics' and tag:
            entities_dict[cat] = {}
            entities_dict[cat][tag] = [entity]
        elif isinstance(entity, list):
            entities_dict[cat] = entity
        else:
            entities_dict[cat] = [entity]


def add_annotated_entities_to_yml(text_with_tags: str, yml_handler: YAMLHandler, filename: str) -> None:
    """Populates YAMLHeader with annotated entities.

    :param str text_with_tags: Text with inserted tags of the MIU.
    :param YAMLHandler yml_handler: YAMLHandler of the MIU.
    :param str filename: Filename of the current MIU (used in error msg).
    """
    # We do not need to differentiate between automated and manual tags
    text_with_tags = text_with_tags.replace('Ü', '')
    tg = Toponyms.instance()
    entity_tags_df = EntityTags.instance().get_entity_tags_df()
    entities_dict = {}
    nas_dict = {}
    toponyms_set: Set[YAMLToponym] = set()
    provinces_set: Set[YAMLToponym] = set()
    nas_counter = 0

    m = ENTITY_TAGS_PATTERN.search(text_with_tags)
    while m:
        tag = m.group('entity')
        length = int(m.group('length'))
        entity = ' '.join(text_with_tags[m.end():].split(maxsplit=length)[:length])

        cat = entity_tags_df.loc[entity_tags_df['TAG'].str.fullmatch(tag), 'CATEGORY'].iloc[0]
        if cat == 'DATE' or cat == 'AGE':
            try:
                val, e_cat = get_yrs_tag_value(m.group(0))
                add_to_entities_dict(entities_dict, cat, {'entity': entity, cat.lower(): val, 'cat': e_cat})
            except ValueError:
                print(f'Tag is neither year nor age: {m.group(0)}\nCheck: {filename}')
                return
        elif cat == 'TOPONYM':
            place, uri, list_of_uris, list_of_provinces = tg.look_up_entity(entity)
            if len(list_of_uris) > 1:
                yml_handler.set_ambigious_toponyms()
            toponyms_set.update(list_of_uris)
            provinces_set.update(list_of_provinces)
            add_to_entities_dict(entities_dict, cat, {'entity': place, 'URI': uri})
        elif cat == 'ONOMASTIC':
            if tag.startswith('SHR') and entity.startswith('ب'):
                entity = entity[1:]
                add_to_entities_dict(entities_dict, cat, entity, tag)
            elif tag.startswith('NAS'):
                nas_dict['nas_' + str(nas_counter)] = entity
                nas_counter += 1
            add_to_entities_dict(entities_dict, cat, entity, tag)
        else:
            add_to_entities_dict(entities_dict, cat, entity, tag)

        m = ENTITY_TAGS_PATTERN.search(text_with_tags, m.end())

    if nas_dict != {}:
        if 'onomastics' in entities_dict.keys():
            entities_dict['onomastics']['nas'] = nas_dict
        else:
            entities_dict['onomastics'] = {'nas': nas_dict}

    if 'onomastics' in entities_dict.keys():
        # Sort dict by keys
        entities_dict['onomastics'] = dict(sorted(entities_dict.get('onomastics').items()))

    if toponyms_set:
        entities_dict['settlements'] = list(toponyms_set)
        entities_dict['edges_settlements'] = [[a, b] for a, b in combinations(toponyms_set, 2)]
        provinces_set = set([tg.look_up_province(p) for p in provinces_set])
        entities_dict['provinces'] = list(provinces_set)
        entities_dict['edges_provinces'] = [[a, b] for a, b in combinations(provinces_set, 2)]

    if entities_dict.get('dates'):
        dates = entities_dict.get('dates')
        birth_date = [d.get('date') for d in dates if d.get('cat') == 'B']
        death_date = [d.get('date') for d in dates if d.get('cat') == 'D']
        if death_date:
            entities_dict['max_date'] = max(death_date)
        else:
            entities_dict['max_date'] = max([d.get('date') for d in dates])

        if birth_date:
            entities_dict['min_date'] = min(birth_date)
        else:
            entities_dict['min_date'] = entities_dict.get('max_date') - 70

    yml_handler.add_tagged_entities(entities_dict)
