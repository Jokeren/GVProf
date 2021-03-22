import argparse
import time

from collections import namedtuple

from test_cases import Test
from utils import pipe_read, nsys_profile


class Benchmark(Test):
    Config = namedtuple('Config', ['kernels'])

    def __init__(self, arch, version):
        super().__init__('Benchmark', arch, version)

    def setup(self, choices):
        for choice in choices:
            if choice == 'backprop':
                self._configs[choice] = Benchmark.Config(kernels=['bpnn_adjust_weights_cuda'])

    def _run_impl(self, case_name, version):
        command = Test.cases[case_name].command
        options = Test.cases[case_name].options

        time_start = time.time()
        pipe_read([command] + options)
        time_end = time.time()
        elapse = time_end - time_start

        print('{}/{}: {}s'.format(case_name, version, elapse))

        kernel_times, cuda_api_time = nsys_profile(
            [command] + options, self._configs[case_name].kernels)
        for kernel, kernel_time in kernel_times.items():
            print('{}/{}/{}: {}s'.format(case_name,
                    version, kernel, kernel_time / (1e9)))
        print('{}/{}/cuda_api: {}s'.format(case_name, version, cuda_api_time / (1e9)))

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-c', '--case', help='case name')
parser.add_argument('-v', '--version', default='all', help='benchmark version')
parser.add_argument('-i', '--iterations', type=int, default=1)
parser.add_argument('-a', '--arch', choices=['sm_70', 'sm_72',
                    'sm_75', 'sm_80', 'sm_85'], default='sm_70', help='gpu arch name')
args = parser.parse_args()

choice = None if args.case is None else [args.case]

benchmark = Benchmark(args.arch, args.version)
benchmark.setup(choice)
benchmark.run(args.iterations)