"""Unit tests for the ReplyBuffer class."""
import os
import numpy as np
from unittest import TestCase
from ..replay_queue_np import ReplayQueue


# the name of the directory housing this module
DIR = os.path.dirname(os.path.realpath(__file__))


def ones() -> tuple:
    """Return an arbitrary state of ones."""
    s = np.ones((84, 84, 4))
    a = 1
    r = 1
    d = True
    s2 = np.ones((84, 84, 4))
    return s, a, r, d, s2


def zeros() -> tuple:
    """Return an arbitrary state of zeros."""
    s = np.zeros((84, 84, 4))
    a = 0
    r = 0
    d = False
    s2 = np.zeros((84, 84, 4))
    return s, a, r, d, s2


def random_state() -> tuple:
    """Return an arbitrary randomized state"""
    s = np.random.randint(0, 256, (84, 84, 4)).astype('uint8')
    a = np.random.randint(6)
    r = np.random.randint(2) - 1
    d = bool(np.random.randint(1))
    s2 = np.random.randint(0, 256, (84, 84, 4)).astype('uint8')
    return s, a, r, d, s2


class ReplyBuffer__init__(TestCase):
    def test(self):
        self.assertIsInstance(ReplayQueue(10), object)
        self.assertIsInstance(ReplayQueue(size=10), object)


class ReplyBuffer__repr__(TestCase):
    def test(self):
        self.assertEqual('ReplayQueue(size=4321)', repr(ReplayQueue(4321)))
        self.assertEqual('ReplayQueue(size=1234)', repr(ReplayQueue(size=1234)))


class ReplyBuffer__len__(TestCase):
    def test(self):
        arb = ReplayQueue(10)
        self.assertEqual(0, len(arb))
        arb.push(*zeros())
        self.assertEqual(1, len(arb))

        for index in range(2, 30):
            if index < 10:
                arb.push(*zeros())
                self.assertEqual(index, len(arb))
            else:
                arb.push(*ones())
                self.assertEqual(10, len(arb))

        self.assertTrue(ones(), arb.current())


class ReplyBuffer_is_bound(TestCase):
    def test(self):
        arb = ReplayQueue(10)
        for i in range(25):
            # a different item is added so that it will be at the bottom
            # when the loop finishes
            if i == 15:
                arb.push(*ones())
            else:
                arb.push(*zeros())

        # there should only be 10 elements
        self.assertEqual(10, len(arb))
        # it should move the items along as new ones are added
        self.assertEqual(ones()[1], arb.current()[1])


class ReplyBuffer_sample(TestCase):
    def test(self):
        arb = ReplayQueue(1000)
        for i in range(1000):
            arb.push(*ones())

        s, a, r, d, s2 = arb.sample()

        sample_size = len(s)

        exp_s, exp_a, exp_r, exp_d, exp_s2 = ones()

        self.assertEqual([exp_a] * sample_size, list(a))
        self.assertEqual([exp_r] * sample_size, list(r))
        self.assertEqual([exp_d] * sample_size, list(d))

        for index in range(sample_size):
            self.assertTrue(np.array_equal(exp_s, s[index]))
            self.assertTrue(np.array_equal(exp_s2, s2[index]))


class ReplyBuffer_sample_random(TestCase):
    def test(self):
        np.random.seed(1)
        arb = ReplayQueue(1000)
        for i in range(1000):
            arb.push(*random_state())

        s, a, r, d, s2 = arb.sample()

        # save the arrays as the expected arrays
        # np.save('{}/arrays/s_np.npy'.format(DIR), s)
        # np.save('{}/arrays/a_np.npy'.format(DIR), a)
        # np.save('{}/arrays/r_np.npy'.format(DIR), r)
        # np.save('{}/arrays/d_np.npy'.format(DIR), d)
        # np.save('{}/arrays/s2_np.npy'.format(DIR), s2)

        # load the expected arrays
        exp_s = np.load('{}/arrays/s_np.npy'.format(DIR))
        exp_a = np.load('{}/arrays/a_np.npy'.format(DIR))
        exp_r = np.load('{}/arrays/r_np.npy'.format(DIR))
        exp_d = np.load('{}/arrays/d_np.npy'.format(DIR))
        exp_s2 = np.load('{}/arrays/s2_np.npy'.format(DIR))

        # check that the returned arrays are the expected ones
        self.assertTrue(np.array_equal(exp_s, s))
        self.assertTrue(np.array_equal(exp_a, a))
        self.assertTrue(np.array_equal(exp_r, r))
        self.assertTrue(np.array_equal(exp_d, d))
        self.assertTrue(np.array_equal(exp_s2, s2))