from typing import Dict, List, Optional, Set, Tuple, Union, Iterator

from itertools import combinations
from operator import itemgetter
from os import makedirs
from os.path import dirname, split, splitext

from camel_tools.utils.charsets import UNICODE_PUNCT_CHARSET
from pandas import DataFrame, notna

from eis1600.gazetteers.Toponyms import Toponyms
from eis1600.helper.logging import setup_logger
from eis1600.markdown.EntityTags import EntityTags
from eis1600.markdown.markdown_methods import get_yrs_tag_value
from eis1600.markdown.markdown_patterns import ENTITY_TAGS_PATTERN, MIU_HEADER_PATTERN, NEWLINES_CROWD_PATTERN
from eis1600.miu.HeadingTracker import HeadingTracker
from eis1600.repositories.repo import GAZETTEERS_REPO
from eis1600.yml.YAMLHandler import YAMLHandler

__log_filename_nasab = GAZETTEERS_REPO + 'logs/nasab_known.log'
makedirs(dirname(__log_filename_nasab), exist_ok=True)
LOGGER_NASAB_KNOWN = setup_logger('nasab_known', __log_filename_nasab)
LOGGER_TOPONYMS_UNKNOWN = setup_logger('toponyms_unknown', GAZETTEERS_REPO + 'logs/toponyms_unknown.log')


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


def extract_yml_header_and_text(miu_text_line_iter: Iterator, is_header: Optional[bool] = False) -> (str, str):
    """ Returns the YAML header and the text as a tuple from MIU file object.

    Splits the MIU file into a tuple of YAML header and text.
    :param Iterator miu_text_line_iter: Iterator of lines over the MIU file from which to extract YAML header and text.
    :param bool is_header: Indicates if the current MIU is the YAML header of the whole work and if so skips
    removing blank lines, defaults to False.
    :return (str, str): Tuple of the extracted YAML header and text.
    """
    text = ''
    miu_yml_header = ''
    for line in miu_text_line_iter:
        if MIU_HEADER_PATTERN.match(line):
            # Omit the #MIU#Header# line as it is only needed inside the MIU.EIS1600 file, but not in YMLDATA.yml
            next(miu_text_line_iter)
            line = next(miu_text_line_iter)
            miu_yml_header = ''
            while not MIU_HEADER_PATTERN.match(line):
                miu_yml_header += line
                line = next(miu_text_line_iter)
            # Omit the empty line between the header content and the #MIU#Header# line
            miu_yml_header = miu_yml_header[:-2]
            # Skip empty line after #MIU#Header#
            next(miu_text_line_iter)
        else:
            text += line
        # Replace new lines which separate YAML header from text
        if not is_header:
            text = NEWLINES_CROWD_PATTERN.sub('\n\n', text)

    return miu_yml_header, text


def add_to_entities_dict(
        entities_dict: Dict,
        cat: str,
        entity: Union[str, Tuple[str, Union[int, str]], List[Tuple[str, str]], List[str], Tuple[int, str], Dict],
        tag: Optional[str] = None
) -> None:
    """Add a tagged entity to the respective list in the entities_dict.

    :param Dict entities_dict: Dict containing previous tagged entities.
    :param str cat: Category of the entity.
    :param Union[str|int] entity: Entity - might be int if entity is a date, otherwise str.
    :param str tag: Optional, onomastic classification used to differentiate between onomastic elements, defaults to
    None.
    """
    cat = cat.lower() + 's'
    if tag:
        tag = tag.lower()
    if cat in entities_dict.keys():
        if cat == 'onomastics' and tag:
            if tag in entities_dict[cat].keys():
                entities_dict[cat][tag].add(entity)
            else:
                entities_dict[cat][tag] = {entity}
        else:
            entities_dict[cat].append(entity)
    else:
        if cat == 'onomastics' and tag:
            entities_dict[cat] = {}
            entities_dict[cat][tag] = {entity}
        elif isinstance(entity, list):
            entities_dict[cat] = entity
        else:
            entities_dict[cat] = [entity]


def add_annotated_entities_to_yml(
        df: DataFrame,
        yml_handler: YAMLHandler,
        file_path: str,
        reconstructed_miu_text_with_tags: str
) -> None:
    """Populates YAMLHeader with annotated entities.

    Extract annotated entities as metadata. While doing so, identify toponyms and calculate active period for the
    biographee.
    :param DataFrame df: DataFrame with two columns 'TAGS_LISTS' and 'TOKENS'.
    :param YAMLHandler yml_handler: YAMLHandler of the MIU.
    :param str file_path: Filename of the current MIU (used in error msg).
    """
    # We do not need to differentiate between automated and manual tags
    entity_tags_df = EntityTags().get_entity_tags_df()
    entities_dict = {}
    nas_dict = {}
    nas_counter = 0
    settlements_set: Set[str] = set()
    provinces_set: Set[str] = set()
    ambiguous_toponyms = False

    # Get all tags with their information extracted into individual elements
    s_notna = df['TAGS_LISTS'].loc[df['TAGS_LISTS'].notna()].apply(lambda tag_list: ','.join(tag_list))
    df_matches = s_notna.str.extractall(ENTITY_TAGS_PATTERN).dropna(how='all')

    # Interpret extracted information for each tag
    for index_tuple, row in df_matches.iterrows():
        # Since there can be multiple tags for the same tokens df_matches has a multi-index
        index = index_tuple[0]
        tag = row['entity']
        length = int(row['length'])
        sub_cat = row['sub_cat']
        try:
            entity = ' '.join(df['TOKENS'].iloc[index:index + length].to_list())
        except TypeError:
            print(f'Something is at odd here: {row["full_tag"]}\nCheck: {file_path}')
            yml_handler.set_error_while_collecting_annotated_entities(row["full_tag"])
            return
        cat = entity_tags_df.loc[entity_tags_df['TAG'].str.fullmatch(tag), 'CATEGORY'].iloc[0]

        if cat == 'DATE' or cat == 'LUNAR_MONTH' or cat == 'AGE':
            # TODO what about the month? ATM, they are not collected into the yml. If you want to change that,
            #  add 'month' (or maybe lunar_month) to YAMLHandler line 27!
            try:
                val, e_cat = get_yrs_tag_value(row['full_tag'])
                add_to_entities_dict(entities_dict, cat, {'entity': entity, cat.lower(): val, 'cat': e_cat})
            except ValueError:
                print(
                        f'Tag is neither year nor age: {row["full_tag"]}\nCheck: {file_path}\n'
                        f'{reconstructed_miu_text_with_tags}'
                )
                yml_handler.set_error_while_collecting_annotated_entities(row["full_tag"])
                return
        elif cat == 'TOPONYM':
            # Identify toponym
            place, uris_tag, list_of_uris, list_of_provinces = Toponyms().look_up_entity(entity)
            if notna(sub_cat):
                add_to_entities_dict(entities_dict, cat, {'entity': place, 'URI': uris_tag, 'cat': sub_cat})
            else:
                add_to_entities_dict(entities_dict, cat, {'entity': place, 'URI': uris_tag})
            if len(list_of_uris) == 0:
                path, uri = split(file_path)
                uri, ext = splitext(uri)
                LOGGER_TOPONYMS_UNKNOWN.info(f'{uri},{entity}')
            else:
                if len(list_of_provinces) > 0:
                    settlements_set.update(list_of_uris)
                    provinces_set.update(list_of_provinces)
                else:
                    # if there is no province URI that means the toponym is a province and should therefore be added
                    # to provinces and not settlements
                    provinces_set.update(list_of_uris)
                if len(list_of_uris) > 1:
                    # The toponym is ambiguous and matched multiple entries in our gazetteer
                    ambiguous_toponyms = True
        elif cat == 'PERSON' or cat == 'BOOK':
            if notna(sub_cat):
                add_to_entities_dict(entities_dict, cat, {'entity': entity, 'cat': sub_cat}, tag)
            else:
                print(
                    f'Tag is missing the sub-classification: {row["full_tag"]}\nCheck: {file_path}\n'
                    f'{reconstructed_miu_text_with_tags}'
                    )
                yml_handler.set_error_while_collecting_annotated_entities(row["full_tag"])
                add_to_entities_dict(entities_dict, cat, {'entity': entity, 'cat': 'X'}, tag)
        elif cat == 'ONOMASTIC':
            if tag.startswith('SHR') and entity.startswith('ب'):
                entity = entity[1:]
                add_to_entities_dict(entities_dict, cat, entity, tag)
            elif tag.startswith('NAS'):
                nas_dict['nas_' + str(nas_counter)] = entity
                nas_counter += 1
            else:
                add_to_entities_dict(entities_dict, cat, entity, tag)
            LOGGER_NASAB_KNOWN.info(f'{tag},{entity}')
        else:
            add_to_entities_dict(entities_dict, cat, entity, tag)

    if nas_dict != {}:
        if 'onomastics' in entities_dict.keys():
            entities_dict['onomastics']['nas'] = nas_dict
        else:
            entities_dict['onomastics'] = {'nas': nas_dict}

    if 'onomastics' in entities_dict.keys():
        # Sort dict by keys
        entities_dict['onomastics'] = dict(
                sorted(
                        [(k, list(v)) if isinstance(v, set) else (k, v) for k, v in
                         entities_dict.get('onomastics').items()],
                        key=itemgetter(0)
                )
        )

    # Generate edges
    if settlements_set:
        entities_dict['settlements'] = list(settlements_set)
        entities_dict['edges_settlements'] = [[a, b] for a, b in combinations(settlements_set, 2) if a != b]
    if provinces_set:
        entities_dict['provinces'] = list(provinces_set)
        entities_dict['edges_provinces'] = [[a, b] for a, b in combinations(provinces_set, 2) if a != b]

    # Extrapolate active period for the biographee
    # TODO dates_headings are not analysed yet
    if entities_dict.get('dates'):
        dates = entities_dict.get('dates')
        birth_date = [d.get('date') for d in dates if d.get('cat') == 'B']
        death_date = [d.get('date') for d in dates if d.get('cat') == 'D']
        alternative_dates = [d.get('date') for d in dates]
        age_at_death = None
        if entities_dict.get('ages') and [a.get('age') for a in entities_dict.get('ages') if a.get('cat') == 'D']:
            age_at_death = max([a.get('age') for a in entities_dict.get('ages') if a.get('cat') == 'D'])

        if death_date:
            entities_dict['max_date'] = max(death_date)
        elif birth_date:
            if age_at_death:
                entities_dict['max_date'] = min(birth_date) + age_at_death
            else:
                # TODO better approximation for active period
                entities_dict['max_date'] = min(birth_date) + 70
        elif alternative_dates:
            entities_dict['max_date'] = max(alternative_dates)

        if birth_date:
            entities_dict['min_date'] = min(birth_date)
        elif entities_dict.get('max_date'):
            if type(age_at_death) == 'int':
                entities_dict.get('max_date') - age_at_death
            else:
                # TODO better approximation for active period
                entities_dict['min_date'] = entities_dict.get('max_date') - 70

    # Entities, which are not listed in 'YAMLHandler.__attr_from_annotation' are ignored
    yml_handler.add_tagged_entities(entities_dict)
    if ambiguous_toponyms:
        yml_handler.set_ambiguous_toponyms()


def add_statistics_to_yml(
        df: DataFrame,
        yml_handler: YAMLHandler,
) -> None:
    tokens_without_punctuation_df = df['TOKENS'].loc[df['TOKENS'].notna() & ~df['TOKENS'].isin(UNICODE_PUNCT_CHARSET)]
    # Count() counts all non-na values and returns Decimal, not int - jsonpickle skips decimal type,
    # therefore convert to int
    yml_handler.add_number_of_tokens(int(tokens_without_punctuation_df.count()))
