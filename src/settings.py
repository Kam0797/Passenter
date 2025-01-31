# Copyright (C) 2025 Kam <gv.kamal2003@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


# dont delete this file , var defs here..
import os
from pathlib import Path

INPUT_FILE_PATH = ''

FILE_NAME,TEXT_FILE,OUTPUT_FILE = '','',''
INPUT_DIR_PATH = ''
TEXT_OUTPUT_DIR = ''
SPREADSHEET_OUTPUT_DIR = ''
atr_merge = False

root_file = os.path.abspath(__file__)
root_path = Path(root_file).parent.parent
