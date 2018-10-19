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
import json
import copy


class WikiSQLTeacher(DialogTeacher):
    def __init__(self, opt, shared=None):
        # store datatype

        self.agg_ops = ['', 'MAX', 'MIN', 'COUNT', 'SUM', 'AVG']
        self.cond_ops = ['=', '>', '<', 'OP']
        self.syms = ['SELECT', 'WHERE', 'AND', 'COL', 'TABLE', 'CAPTION', 'PAGE',
                     'SECTION', 'OP', 'COND', 'QUESTION',
                     'AGG',
                     'AGGOPS', 'CONDOPS']

        self.dt = opt['datatype'].split(':')[0]

        # store identifier for the teacher in the dialog
        self.id = 'wikisql'

        build(opt)
        opt['datafile'] = os.path.join(opt['datapath'], 'WikiSQL')
        self.opt = copy.deepcopy(opt)

        super().__init__(opt, shared)

    def setup_data(self, input_path):

        print('loading: ' + input_path)

        new_episode = True

        table_file_path = os.path.join(input_path, 'data', 'train.tables.jsonl')
        qa_file_path = os.path.join(input_path, 'data', 'train.jsonl')
        data = []
        with open(table_file_path) as table_file:
            table_data = [json.loads(jline) for jline in table_file]
            table_data = {table['id']: table for table in table_data}

        with open(qa_file_path) as qa_file:
            qa_data = [json.loads(jline) for jline in qa_file]

        def parse_into_sql(table, query):
            header = table['header']

            sql_query = 'SELECT {agg} {sel} FROM table'.format(
                agg=self.agg_ops[query['agg']],
                sel=header[query['sel']],
            )
            if query['conds']:
                sql_query += ' WHERE ' + ' AND '.join(
                    ['{} {} {}'.format(header[i], self.cond_ops[o], v) for i, o, v in
                     query['conds']])
            return sql_query

        def table_into_context(table):
            header = table['header']
            if len(header) == 0:
                return 'The table has no columns'
            elif len(header) == 1:
                return 'The table has column {}'.format(header[0])
            else:
                return 'The table has column names {} and {}.'.format(
                    ', '.join(header[:-1]), header[-1])

        for line in qa_data:
            id = line["table_id"]
            question = line["question"]
            table = table_data[id]

            context = table_into_context(table)
            sql = parse_into_sql(table, line["sql"])

            yield (context + '\n' + question, [sql], None, None), new_episode


class DefaultTeacher(WikiSQLTeacher):
    pass
