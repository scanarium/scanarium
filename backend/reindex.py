#!/usr/bin/env python3

import os
import logging
import sys

SCANARIUM_DIR_ABS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCANARIUM_DIR_ABS)
from scanarium import Scanarium
del sys.path[0]

logger = logging.getLogger(__name__)


def reindex(scanarium):
    dynamic_scenes_dir = os.path.join(
        scanarium.get_dynamic_directory(), 'scenes')
    scenes_dir_abs = scanarium.get_scenes_dir_abs()
    for scene in os.listdir(scenes_dir_abs):
        if os.path.isdir(os.path.join(scenes_dir_abs, scene)):
            logging.debug(f'Reindexing scene "{scene}" ...')
            dynamic_scene_dir = os.path.join(dynamic_scenes_dir, scene)
            if not os.path.isdir(dynamic_scene_dir):
                os.makedirs(dynamic_scene_dir)
            scanarium.reindex_actors_for_scene(scene)


if __name__ == "__main__":
    scanarium = Scanarium()
    scanarium.handle_arguments('Reindexes dynamic content, such as actors')
    scanarium.call_guarded(reindex)
