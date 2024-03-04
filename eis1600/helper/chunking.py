from re import search
from os import remove
from typing import List
from os.path import splitext, getsize, exists
from itertools import groupby

from eis1600.repositories.repo import SPLITTED_PART_NAME_INFIX, get_part_filepath
from eis1600.texts_to_mius.check_formatting_methods import check_file_split
from eis1600.markdown.markdown_patterns import HEADER_END_PATTERN, MISSING_DIRECTIONALITY_TAG_PATTERN, \
    FIRST_LEVEL_HEADING_PATTERN
from eis1600.texts_to_mius.subid_methods import pre_clean_text


def resize_chunks(chunks: List[str], n: int = 400_000) -> List[str]:
    """ If there are chunks with size smaller than n, merge them in groups to avoid having too many tiny files.

    :param list chunks: chunks of text.
    :param int n: soft maximum number of characters per chunk.
    :return list: modified chunking.
    """
    new_chunks = []
    aux = ""
    for chunk in chunks:
        if len(aux) > n:
            new_chunks.append(aux)
            aux = ""
        if aux:
            aux += "\n\n"
        aux += chunk
    if aux:
        # if the last piece of text is too small, add it to the last
        if len(aux) < n // 2 and new_chunks:
            new_chunks[-1] += f"\n\n{aux}"
        else:
            new_chunks.append(aux)
    return new_chunks


def split_file(infile: str, max_size: int, debug: bool = False):
    """ Break files larger or equal MB indicated in max_size into parts so that they can be processed separately.
    All chunks will share the same header.


    :param str infile: Path of the file to split.
    :param int max_size: Maximum size of file in megabytes. If file is larger, it is splitted in parts.
        I max_size is -1, do not split.
    :param bool debug: show warnings.
    :return None:
    """
    if SPLITTED_PART_NAME_INFIX in infile:
        return

    file_path, file_ext = splitext(infile)

    # remove previous splitting
    i = 1
    while exists(old_part_file := get_part_filepath(file_path, i, file_ext)):
        remove(old_part_file)
        i += 1

    if max_size == -1:
        return

    if (getsize(infile) >> 20) < max_size:
        return

    with open(infile, 'r', encoding='utf8') as infile_h:
        text = infile_h.read()

        header_and_text = HEADER_END_PATTERN.split(text)
        header = header_and_text[0] + header_and_text[1]
        text = header_and_text[2].lstrip('\n')  # Ignore new lines after #META#Header#End#
        text = pre_clean_text(text)
        text = MISSING_DIRECTIONALITY_TAG_PATTERN.sub('\g<1>_ء_ \g<2>', text)

        paragraphs = text.split('\n\n')

        blocks = [(k, list(gr)) for k, gr in groupby(
            paragraphs,
            lambda s: bool(search(FIRST_LEVEL_HEADING_PATTERN, s))
        )]

        chunks = []

        aux = []
        for is_fst_header, paragraphs in blocks:
            if is_fst_header:
                #if debug and len(paragraphs) > 1:
                #    multiple_headings = "\n\n".join(paragraphs)
                #    print(f"\nfile {infile} has consecutive first level multiple_headings:"
                #          f"\n\n{multiple_headings}")
                if len(aux) > 1:
                    chunks.append("\n\n".join(aux))
                    aux = []
            for paragraph in paragraphs:
                aux.append(paragraph)

        if aux:
            chunks.append("\n\n".join(aux))

        # to avoid having too many small files
        chunks = resize_chunks(chunks)

        # there is only one first level heading in all the file
        if len(chunks) > 1:

            for i, chunk in enumerate(chunks, 1):

                final = header + '\n\n' + chunk
                if final[-1] != '\n':
                    final += '\n'

                outfile_path = get_part_filepath(file_path, i, file_ext)
                with open(outfile_path, 'w', encoding='utf8') as outfp:
                    outfp.write(final)

            check_file_split(infile, debug)