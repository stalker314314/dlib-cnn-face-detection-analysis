#!/usr/bin/env python3

import functools
import os
import time
import resource
import subprocess

import numpy as np
from PIL import Image
from enum import Enum
from typing import Tuple

MAX_MEMORY = 8 * 1024  # 8GB


class ImageTypes(Enum):
    BLACK = 1,
    RANDOM = 2,
    FACES = 3


def generate_image(width: int, height: int, image_type: ImageTypes) -> str:
    if image_type == ImageTypes.BLACK:
        image_data = np.zeros((height, width, 3), dtype=np.uint8)
        img = Image.fromarray(image_data)
    elif image_type == ImageTypes.RANDOM:
        image_data = np.array(np.random.rand(height, width, 3)) * 256
        image_data = np.asarray(image_data, dtype=np.uint8)
        img = Image.fromarray(image_data)
    else:
        img = Image.open('faces.jpg')
        img.thumbnail((width, height), Image.ANTIALIAS)
    img.save('image.png')
    return 'image.png'


def set_limits(memory_in_mb: int) -> None:
    resource.setrlimit(resource.RLIMIT_AS, (memory_in_mb * 1024 * 1024, memory_in_mb * 1024 * 1024))


def get_limit_for_size(from_memory: int, to_memory: int, width: int, height: int,
                       image_type: ImageTypes, upsample_num: int) -> Tuple[int, int, int]:
    image_file = generate_image(width, height, image_type)
    max_memory_not_working = from_memory
    min_memory_working = to_memory
    duration = 0
    faces_found = -1
    while min_memory_working - max_memory_not_working > 128:
        mem = max_memory_not_working + int((min_memory_working - max_memory_not_working) / 2)
        start_time = time.time()
        p = subprocess.Popen(['python3', 'test-program.py', image_file, str(upsample_num)],
                             preexec_fn=functools.partial(set_limits, mem),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        out, _ = p.communicate()
        if p.returncode == 0:
            duration = max(int(time.time() - start_time), 0)
            start_index = str(out).index('Faces found')
            end_index = str(out)[start_index:].index('\\n')
            faces_found = int(str(out)[start_index+12:start_index+end_index])
            min_memory_working = mem
        else:
            max_memory_not_working = mem
    os.remove(image_file)
    return min_memory_working, duration, faces_found


def main():
    for width in range(100, 3800, 100):
        height = int((3 * width) / 4)
        for image_type in ImageTypes:
            for upsample_num in range(0, 2):
                memory, duration, faces_found = get_limit_for_size(1, MAX_MEMORY, width, height, image_type, upsample_num)
                print('width= {} height= {} type= {} upsample= {} => memory= {} duration= {} faces= {}'.format(
                    width, height, image_type, upsample_num, memory, duration, faces_found))
    # This is how we can get ratio compared to duration
    # import math
    # area = 3000000
    # for ratio in (1/4, 1/1.5, 1/2, 1, 1.5, 2, 4):
    #     width = int(math.sqrt(area/ratio))
    #     height = int(area/width)
    #     memory, duration, faces_found = get_limit_for_size(
    #         MAX_MEMORY-150, MAX_MEMORY, width, height, ImageTypes.BLACK, 0)
    #     print('width= {} height= {} duration= {}'.format(width, height, duration))


if __name__ == '__main__':
    main()
