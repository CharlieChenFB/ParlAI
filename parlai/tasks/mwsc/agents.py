#!/usr/bin/env python3

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
# Download and build the data if it does not exist.

from parlai.core.teachers import DialogTeacher
from .build import build
import os
import re


class MWSCTeacher(DialogTeacher):
    def __init__(self, opt, shared=None):
        # store datatype
        self.dt = opt['datatype'].split(':')[0]

        # store identifier for the teacher in the dialog
        self.id = 'mwsc'

        build(opt)
        opt['datafile'] = os.path.join(opt['datapath'], 'MWSC')
        super().__init__(opt, shared)

    def setup_data(self, input_path):
        print('loading: ' + input_path)
        file_path = os.path.join(input_path, 'schema.txt')

        new_episode = True

        with open(file_path) as file:
            data = file.read()[:-1].split('\n\n')

        def parse_square_bracket(input_data):
            output = re.split('\]|/|\[', input_data)
            if len(output) == 1:
                return output * 2
            else:
                return [''.join(output[:1] + output[2:]),
                        ''.join(output[:2] + output[3:])]

        for qa in data:

            context, question, answer = qa.split('\n')
            context = parse_square_bracket(context)
            question = parse_square_bracket(question)
            answer = answer.split('/')
            for i in range(2):
                yield (context[i] + '\n' + question[i],
                       [answer[i]], None, None), new_episode


class DefaultTeacher(MWSCTeacher):
    pass
