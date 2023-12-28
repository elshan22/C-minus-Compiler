"""
    Programming Assignment 3 :
    Intermediate Code Generating
    + Semantic Analysis (Optional)
    ++ Function 3AC Translation (Optional)
    Compiler Design Course
    Fall of 1401
    lecturer: Samaneh Hosseinmardi

    def get_contributors() -> Tuple[List[str, int], List[str, int]]:
        return
            ['Mahdi Saber', 99105526],
            ['Parsa Enayati', 99105623]
"""
from typing import List

import anytree

from parse import Parser


def write_parse_tree(root: anytree.Node) -> None:
    file = open('parse_tree.txt', mode='w', encoding='utf-8')
    lines = []
    for pre, _, node in anytree.RenderTree(root):
        lines.append(f'{pre}{node.name}')
    file.write('\n'.join(lines))
    file.close()


def write_syntax_errors(syntax_errors: List[str]) -> None:
    file = open('syntax_errors.txt', 'w')
    file.write('\n'.join(syntax_errors))
    if not len(syntax_errors):
        file.write('There is no syntax error.')
    file.close()


def write_output(program_block: list) -> None:
    file = open('output.txt', 'w')
    program_block = list(filter(lambda x: x[0], program_block))
    for i, pb in enumerate(program_block):
        pb = '(' + ', '.join(list(map(str, (filter(lambda x: x, pb))))) + ')'
        file.write(f'{i}\t{pb}\n')
    file.close()


if __name__ == '__main__':
    parser = Parser('input.txt')
    write_parse_tree(parser.get_parse_tree())
    write_syntax_errors(parser.get_syntax_errors())
    write_output(parser.code_generator.program_block)
