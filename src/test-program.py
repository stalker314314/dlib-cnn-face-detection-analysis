#!/usr/bin/env python3

import sys
import dlib


def main(image_file, upsample_num):
    cnn_face_detector = dlib.cnn_face_detection_model_v1('mmod_human_face_detector.dat')
    img = dlib.load_rgb_image(image_file)
    dets = cnn_face_detector(img, upsample_num)
    return len(dets)


if __name__ == '__main__':
    faces = main(sys.argv[1], int(sys.argv[2]))
    print('Faces found:{}'.format(faces))
    exit(0)
