# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from .service import generate_new_datasets


class ServiceTest(TestCase):
    def setUp(self):
        self.datasets = [
            {
                'name': 'time',
                'data': '0010, 0020, 0030, 0040, 0050, 0100',
                'list': ['0010', '0020', '0030', '0040', '0050', '0100'],
                'color': 'black',
            },
            {
                'name': 'Load',
                'data': '10.0, 20.0, 30.0, 40.0, 50.0, 60.0',
                'list': ['10.0', '20.0', '30.0', '40.0', '50.0', '60.0'],
                'color': 'red',
            }
        ]

    def test_generate_new_datasets(self):
        updated_datsets = generate_new_datasets(datasets=self.datasets,
                                                queries=['Solar|yellow=2*i1', 'Export|blue=-i1'])
        self.assertEqual(len(updated_datsets), 4)
        self.assertEqual(updated_datsets[2]['name'], 'Solar')
        self.assertEqual(updated_datsets[2]['list'][0], '20.0')
        self.assertEqual(updated_datsets[3]['name'], 'Export')
        self.assertEqual(updated_datsets[3]['list'][0], '-10.0')
