"""
# beNNch - Unified execution, collection, analysis and
comparison of neural network simulation benchmarks.
Copyright (C) 2021 Forschungszentrum Juelich GmbH, INM-6

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.

SPDX-License-Identifier: GPL-3.0-or-later
"""

import sys
import os

from nbformat import v4 as nbf
import nbformat
from IPython.display import Image
from IPython.display import HTML

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from analysis.plot_helper import plot


def display_plot(timer_hash, plot_path, attributes, page_number=1):
    display_list = '<left><ul>\n'
    file_path = os.popen(
        f"find . -name '*{timer_hash}.csv'").read().strip()
    for attribute in attributes:
        value = os.popen(
            f'git annex metadata "{file_path}" '
            + f'--get {attribute}').read().strip()
        display_list += f'  <li>{attribute}: {value}</li>\n'
    display_list += '</ul></left>'

    display(HTML(f'<center><header>benchmark ID: {timer_hash}</header></center>'))
    display(Image(filename=os.path.join(plot_path, timer_hash + '.png')))
    display(HTML(display_list))
    display(HTML(f'<center>page {page_number}</center>'))


def make_notebook(outPath: str, timer_hashes, attributes_to_display):
    nb = nbf.new_notebook()
    cells = []
    codes = {
        'skip': ["import sys",
                 "import os",
                 "sys.path.insert(1, os.path.join(sys.path[0], '..'))",
                 "from slideshow.slideshow import display_plot"],
        'slide': [f"display_plot('{timer_hashes[0]}', "
                  + "'./plots', "
                  + f"{attributes_to_display})"],
        'subslide': []
    }

    page_number = 2
    for timer_hash in timer_hashes[1:]:
        codes['subslide'].append(f"display_plot('{timer_hash}', "
                                 + "'./plots', "
                                 + f"{attributes_to_display}, "
                                 + f"{page_number})")
        page_number += 1
    for key, code_list in codes.items():
        for code in code_list:
            cells.append(nbf.new_code_cell(code, metadata={
                         "slideshow": {"slide_type": key}}))

    nb['cells'] = cells

    fname = 'flipbook.ipynb'
    with open(os.path.join(outPath, fname), 'w') as _:
        nbformat.write(nb, _)


if __name__ == '__main__':

    scaling_type = sys.argv[1]
    attributes_to_display = sys.argv[2:]

    csv_files = os.popen(
        "find . -not -path '*/.*' -name '*.csv' | sort").read().strip().split(
            '\n')
    timer_hashes = []
    os.system('mkdir -p ./plots')

    for csv_file in csv_files:
        timer_hash = csv_file.split('/')[-1].split('.')[0]
        timer_hashes.append(timer_hash)
        plot(scaling_type=scaling_type,
             timer_hash=timer_hash,
             timer_file=csv_file,
             save_path='./plots'
             )
    make_notebook('./', timer_hashes, attributes_to_display)
    os.system("jupyter nbconvert --inplace --execute flipbook.ipynb")
    os.system("jupyter nbconvert --to slides flipbook.ipynb "
              + "--TemplateExporter.exclude_input=True "
              + "--SlidesExporter.reveal_transition='none'")
    os.system("rm flipbook.ipynb")
    # os.system("rm -r ./plots")
