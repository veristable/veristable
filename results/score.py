import os
import re
import tqdm
# from statistics import median
from pprint import pprint

TIMEOUT = 900
EXTRA_POINT = False

TOOLS = ['mnbab', 'marabou', 'nnenum', 'abcrown', 'neuralsat', 'veristable']
BENCHMARKS = ['acasxu', 'mnistfc', 'cifar2020', 'sri_resnet_a', 'sri_resnet_b', 'mnist_gdvb']
BENCHMARK_FOLDERS = {t: {b: b for b in BENCHMARKS} for t in TOOLS}


BENCHMARK_FOLDERS = {t : { v: k for k, v in tt.items()} for t, tt in BENCHMARK_FOLDERS.items()}
# pprint(BENCHMARK_FOLDERS)

VALID_RESULT_FILES = {b: [] for b in BENCHMARKS}
for b in BENCHMARKS:
    for line in open(f'../benchmark/{b}/instances.csv').read().strip().split('\n'):
        # print(line)
        net, spec = line.split(',')[:-1]
        net = os.path.basename(net)[:-5]
        spec = os.path.basename(spec)[:-7]
        res = f'net_{net}_spec_{spec}'
        VALID_RESULT_FILES[b].append(res.replace('_simplified', ''))
        # VALID_RESULT_FILES[b].append(f'net_{net}_simplified_spec_{spec}')


def recursive_walk(rootdir):
    for r, dirs, files in os.walk(rootdir):
        for f in files:
            yield os.path.join(r, f)
            
            
def check_filename(name):
    for tool in TOOLS:
        if f'/{tool}/' in name:
            return True
    return False

def get_score(score_dict):
    score = 0.0
    score += score_dict['verified'] * 10
    score += score_dict['falsified'] * 1
    if EXTRA_POINT:
        score += score_dict['1st'] * 2
        score += score_dict['2nd'] * 1
    return int(score)

def get_runtime(score_dict):
    return score_dict['runtime']


def assert_status(status):
    if 'sat' in status:
        return 'unsat' not in status
    if 'unsat' in status:
        return 'sat' not in status


def tool_to_latex(tool):
    if tool == 'veristable':
        return '\\tool{}'
    if tool == 'mnbab':
        return '\mnbab{}'
    if tool == 'marabou':
        return '\marabou{}'
    if tool == 'abcrown':
        return '\crown{}'
    if tool == 'nnenum':
        return '\\nnenum{}'
    if tool == 'neuralsat':
        return '\\neuralsat{}'
    print(tool)
    raise
    
def benchmark_to_latex(b):
    if b == 'acasxu':
        return '\multirow{6}{*}{\\rotatebox[origin=c]{90}{ACAS Xu}}'
    if b == 'mnistfc':
        return '\multirow{6}{*}{\\rotatebox[origin=c]{90}{MNISTFC}}'
    if b == 'cifar2020':
        return '\multirow{6}{*}{\\rotatebox[origin=c]{90}{CIFAR2020}} '
    if b == 'sri_resnet_a':
        return '\multirow{6}{*}{\\rotatebox[origin=c]{90}{RESNET\_A}} '
    if b == 'sri_resnet_b':
        return '\multirow{6}{*}{\\rotatebox[origin=c]{90}{RESNET\_B}} '
    if b == 'mnist_gdvb':
        return '\multirow{6}{*}{\\rotatebox[origin=c]{90}{MNIST\_GDVB}} '
    if b == 'overall':
        return '\multirow{6}{*}{\\rotatebox[origin=c]{90}{\\textbf{Overall}}} '
    print(b)
    raise



def network_to_latex(b):
    if b == 'mnist-net-256x6':
        return 'MNIST\_256x6'
    if b == 'mnist-net-256x4':
        return 'MNIST\_256x4'
    if b == 'mnist-net-256x2':
        return 'MNIST\_256x2'

    if b == 'convBigRELU--PGD':
        return 'ConvBigRELU'
    if b == 'cifar10-8-255':
        return 'CIFAR10\_8\_255'
    if b == 'cifar10-2-255':
        return 'CIFAR10\_2\_255'
    
    if b == 'resnet-3b2-bn-mixup-adv-4.0-bs128-lr-1':
        return '3B2\_ADV'
    if b == 'resnet-3b2-bn-mixup-ssadv-4.0-bs128-lr-1-v2':
        return '3B2\_SSADV'
    
    raise



def benchmark_to_latex_runtime(b):
    if b == 'acasxu':
        return '\multirow{2}{*}{ACAS Xu} '
    if b == 'mnistfc':
        return '\multirow{6}{*}{MNISTFC} '
    if b == 'cifar2020':
        return '\multirow{6}{*}{CIFAR2020} '
    if b == 'sri_resnet_a':
        return '\multirow{2}{*}{RESNET\_A} '
    if b == 'sri_resnet_b':
        return '\multirow{2}{*}{RESNET\_B} '
    if b == 'mnist_gdvb':
        return '\multirow{2}{*}{MNIST\_GDVB}'
    print(b)
    raise
# pprint(BENCHMARK_FOLDERS)


INSTANCES_CSV = [_ for _ in recursive_walk('../benchmark/') if _.endswith('instances.csv')]
# print(INSTANCES_CSV)
INSTANCES_BY_BENCHMARK = {b: {} for b in BENCHMARKS}
for csv in INSTANCES_CSV:
    for line in open(csv).read().strip().split('\n'):
        net = os.path.splitext(os.path.basename(line.split(',')[0]))[0].replace('_simplified', '')
        # print(net)
        for b in BENCHMARKS:
            if f'/{b}/' in csv:
                
                if net not in INSTANCES_BY_BENCHMARK[b]:
                    INSTANCES_BY_BENCHMARK[b][net] = 0
                    
                INSTANCES_BY_BENCHMARK[b][net] +=1
                break

# pprint(INSTANCES_BY_BENCHMARK['mnist_gdvb'])
# exit()

RUNTIMES = {tool: {b: {} for b in BENCHMARKS} for tool in TOOLS}
results_file = list([_ for _ in recursive_walk('.') if _.endswith('.res') and check_filename(_)])
# print(results_file)

for file in results_file:
    name = os.path.splitext(os.path.basename(file))[0].replace('_simplified_', '_')
    benchmark_folder = os.path.basename(os.path.dirname(file))
    # if benchmark not in BENCHMARKS:
    #     print(benchmark)
    #     continue
        
    net = name.split('_spec_')[0][4:]
    
    for tool in TOOLS:
        
        benchmark = BENCHMARK_FOLDERS[tool].get(benchmark_folder, None)
        if benchmark not in BENCHMARKS:
            # print('skip', tool, benchmark_folder)
            continue
        
        if name not in VALID_RESULT_FILES[benchmark]:
            # print('skip', file, name)
            # print(VALID_RESULT_FILES[benchmark])
            # exit()
            continue
        
        if net not in INSTANCES_BY_BENCHMARK[benchmark]:
            # print('skip', net)
            # raise
            continue
        
        if net not in RUNTIMES[tool][benchmark]:
            RUNTIMES[tool][benchmark][net] = {}
            
        if f'/{tool}/' in file:
            stat, t = open(file).read().strip().split(',')
            
            if stat.lower() in ['error', 'timeout', 'unknown']:
                continue
            
            if float(t) > TIMEOUT:
                continue
            
            if stat.lower() in ['holds', 'unsat']:
                stat = 'unsat'
            elif stat.lower() in ['violated', 'sat']:
                stat = 'sat'
            else:
                raise ValueError(stat)
            
            RUNTIMES[tool][benchmark][net][name] = stat, float(t)
            break
        
# pprint(RUNTIMES['veristable']['mnist_gdvb'])


SCORES_BY_BENCHMARK = {}
for tool, results in RUNTIMES.items():
    # print('[+]', tool)
    for benchmark, networks in results.items():
        if benchmark not in SCORES_BY_BENCHMARK:
            SCORES_BY_BENCHMARK[benchmark] = {}
        # if tool not in SCORES_BY_BENCHMARK[benchmark]:
        #     SCORES_BY_BENCHMARK[benchmark][tool] = {}
        for net, instances in networks.items():
            if net not in SCORES_BY_BENCHMARK[benchmark]:
                SCORES_BY_BENCHMARK[benchmark][net] = {}
                
            for name, (stat, runtime) in instances.items():
                if name not in SCORES_BY_BENCHMARK[benchmark][net]:
                    SCORES_BY_BENCHMARK[benchmark][net][name] = {}
                
                SCORES_BY_BENCHMARK[benchmark][net][name][tool] = (stat, runtime)
    
# pprint(SCORES_BY_BENCHMARK['mnist_gdvb'])
# exit()


FINAL_SCORES = {}
for benchmark in SCORES_BY_BENCHMARK:
    if benchmark not in FINAL_SCORES:
        FINAL_SCORES[benchmark] = {}

    for net in SCORES_BY_BENCHMARK[benchmark]:
        if net not in FINAL_SCORES[benchmark]:
            FINAL_SCORES[benchmark][net] = {
                tool: {
                    'total': INSTANCES_BY_BENCHMARK[benchmark][net], 
                    'verified': 0, 
                    'falsified': 0, 
                    'solved': 0, 
                    '1st': 0, 
                    '2nd': 0, 
                    'runtime': {
                        'verified': 0.0, 
                        'falsified': 0.0,
                    },
                } for tool in TOOLS
            }

        for name in SCORES_BY_BENCHMARK[benchmark][net]:
            scores = SCORES_BY_BENCHMARK[benchmark][net][name]
            stats = [_[0] for _ in scores.values()]
            assert assert_status(stats), print(name, scores)
            sorted_scores = sorted(scores.items(), key=lambda x: x[1][-1])
            
            fastest = [sorted_scores[0]]
            second_fastest = []
            for ss in sorted_scores:
                if ss not in fastest:
                    if ss[-1][-1] < fastest[0][-1][-1] + 0.2:
                        fastest.append(ss)
                    else:
                        second_fastest.append(ss)    
                        break  
            
            for ss in sorted_scores:
                if ss in fastest+second_fastest:
                    continue
                if ss[-1][-1] < second_fastest[0][-1][-1] + 0.2:
                    second_fastest.append(ss)
                    
            
            # print(scores)
            # print(sorted_scores)
            # print()
            # print(fastest)
            # print(second_fastest)
            # for v, (s_, t_) in scores.items():
            #     FINAL_SCORES[benchmark][net][v]['solved'] += 1
            #     if s_ == 'sat':
            #         FINAL_SCORES[benchmark][net][v]['falsified'] += 1
            #     elif s_ == 'unsat':
            #         FINAL_SCORES[benchmark][net][v]['verified'] += 1
            #     else:
            #         raise NotImplementedError
            #     FINAL_SCORES[benchmark][net][v]['runtime'] += t_
            #     # FINAL_SCORES[benchmark][net][v]['total'] += 1
                
                    
            # for v, (s_, t_) in fastest:
            #     FINAL_SCORES[benchmark][net][v]['1st'] += 1
                
            # for v, (s_, t_) in second_fastest:
            #     FINAL_SCORES[benchmark][net][v]['2nd'] += 1
      
      
            for v, (s_, t_) in scores.items():
                if s_ == 'sat':
                    FINAL_SCORES[benchmark][net][v]['falsified'] += 1
                    FINAL_SCORES[benchmark][net][v]['runtime']['falsified'] += t_
                elif s_ == 'unsat':
                    FINAL_SCORES[benchmark][net][v]['verified'] += 1
                    FINAL_SCORES[benchmark][net][v]['runtime']['verified'] += t_
                else:
                    raise NotImplementedError
                # FINAL_SCORES[benchmark][net][v]['total'] += 1
                
            for v, (s_, t_) in fastest:
                FINAL_SCORES[benchmark][net][v]['1st'] += 1
                
            for v, (s_, t_) in second_fastest:
                FINAL_SCORES[benchmark][net][v]['2nd'] += 1
      
      
# pprint(FINAL_SCORES)  


def get_table_ranking(final_scores):
    ranking_scores = {b: {v: {'score': 0, 'verified': 0, 'falsified': 0, 'fastest': 0, 'solved': 0} for v in TOOLS} for b in final_scores}
    for benchmark in final_scores:
        for net in final_scores[benchmark]:
            for tool in TOOLS:
                score_dict = final_scores[benchmark][net][tool]
                ranking_scores[benchmark][tool]['score'] += get_score(score_dict)
                ranking_scores[benchmark][tool]['verified'] += score_dict['verified']
                ranking_scores[benchmark][tool]['falsified'] += score_dict['falsified']
                if EXTRA_POINT:
                    ranking_scores[benchmark][tool]['fastest'] += score_dict['1st']
            
    # 1 & {\nnenum{}}   & 2130 & 100.0\% & \textbf{139} & \textbf{47} & 90  \\
    # pprint(ranking_scores)
    overall_ranking = {v: {'score': 0, 'verified': 0, 'falsified': 0, 'fastest': 0, 'solved': 0} for v in TOOLS}
    for benchmark, benchmark_scores in ranking_scores.items():
        # print(benchmark, benchmark_scores)
        sorted_benchmark_scores = sorted(benchmark_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        print('\midrule')
        print(benchmark_to_latex(benchmark))
        max_score = sorted_benchmark_scores[0][1]['score']
        for rank_id, tool in enumerate(sorted_benchmark_scores):
            # print('\t', rank_id, tool, tool_to_latex(tool[0]), max_score)
            overall_ranking[tool[0]]['score'] += tool[1]['score']
            overall_ranking[tool[0]]['verified'] += tool[1]['verified']
            overall_ranking[tool[0]]['falsified'] += tool[1]['falsified']
            overall_ranking[tool[0]]['fastest'] += tool[1]['fastest']
            
            line_str = (
                f"& {rank_id + 1} "
                f"& {tool_to_latex(tool[0])} "
                f"& {tool[1]['score']} "
                f"& {tool[1]['score'] / max_score * 100 :.01f}\% "
                f"& {tool[1]['verified']} & {tool[1]['falsified']} "
                
            )
            if EXTRA_POINT:
                line_str += f"& {tool[1]['fastest']} "
            
            line_str += "\\\\"
            print(line_str)


    sorted_overall_ranking = sorted(overall_ranking.items(), key=lambda x: x[1]['score'], reverse=True)
    print('\midrule')
    print(benchmark_to_latex('overall'))
    max_score = sorted_overall_ranking[0][1]['score']
    for rank_id, tool in enumerate(sorted_overall_ranking):
        line_str = (
            f"& {rank_id + 1} "
            f"& {tool_to_latex(tool[0])} "
            f"& {tool[1]['score']} "
            f"& {tool[1]['score'] / max_score * 100 :.01f}\% "
            f"& {tool[1]['verified']} "
            f"& {tool[1]['falsified']} "
        )
        if EXTRA_POINT:
            line_str += f"& {tool[1]['fastest']} "
    
        line_str += "\\\\"
        print(line_str)
    # pass

    
def get_stats():
    results_file = list([_ for _ in recursive_walk('.') if _.endswith('.res') and check_filename(_)])

    # print(len(results_file))

    resdict = {b: {} for b in BENCHMARKS}
    for csv in INSTANCES_CSV:
        for line in open(csv).read().strip().split('\n'):
            line = line.replace('_simplified', '')
            # exit()
            net, spec, _ = line.split(',')
            net = os.path.splitext(os.path.basename(net))[0]
            spec = os.path.splitext(os.path.basename(spec))[0]
            
            name = f'net_{net}_spec_{spec}'
            skip = True
            for b_, v_ in VALID_RESULT_FILES.items():
                if name in v_:
                    skip = False
            
            if skip:
                print(name)
            # exit()
            
            res = [open(_).read().strip().split(',')[0].lower() for _ in results_file if _.replace('_simplified', '').endswith(name + '.res')]
            
            for b in BENCHMARKS:
                if name not in VALID_RESULT_FILES[b]:
                    # print('invalid', name, VALID_RESULT_FILES[b])
                    # exit()
                    continue
                    
                if f'/{b}/' in csv:
                    if net not in resdict[b]:
                        # print(net)
                        resdict[b][net] = {'unsat': 0, 'sat': 0, 'unknown': 0}
                        
                    if 'sat' in res or 'violated' in res:
                        resdict[b][net]['sat'] += 1
                    elif 'unsat' in res or 'holds' in res:
                        resdict[b][net]['unsat'] += 1
                    elif 'timeout' in res:
                        resdict[b][net]['unknown'] += 1
                    else:
                        print(res)
                        raise
    # pprint(resdict)
    return resdict

INSTANCES_DETAIL_BY_BENCHMARK = get_stats()


def get_table_time(final_scores):
    header = '\\textbf{BM} & \\textbf{Networks} &'
    header += ' & '.join([f'\\textbf{{{tool_to_latex(tool)}}}' for tool in TOOLS])
    header += ' \\\\'
    
    print(header)
    # print('\midrule')
    
        
    for benchmark in final_scores:
        print('\midrule')
        if benchmark in ['acasxu', 'mnist_gdvb']:
            line_sat = []
            line_unsat = []
            for tool in TOOLS:
                runtime_sat = 0.0
                runtime_unsat = 0.0
                n_solved_sat = 0
                n_solved_unsat = 0
                for net in final_scores[benchmark]:
                    score_dict = final_scores[benchmark][net][tool]

                    runtime_sat += score_dict['runtime']['falsified']
                    runtime_unsat += score_dict['runtime']['verified']

                    n_solved_sat += score_dict['falsified']
                    n_solved_unsat += score_dict['verified']
                    
                n_unsolved_sat = sum(INSTANCES_DETAIL_BY_BENCHMARK[benchmark][_]["sat"] for _ in INSTANCES_DETAIL_BY_BENCHMARK[benchmark]) - n_solved_sat
                n_unsolved_unsat = sum(INSTANCES_DETAIL_BY_BENCHMARK[benchmark][_]["unsat"] for _ in INSTANCES_DETAIL_BY_BENCHMARK[benchmark]) - n_solved_unsat
                    
                if runtime_sat > 0:
                    line_sat.append(f'{runtime_sat:.01f} ({n_solved_sat}, {n_unsolved_sat})')
                else:
                    line_sat.append(f'-')
                
                if runtime_unsat > 0:
                    line_unsat.append(f'{runtime_unsat:.01f} ({n_solved_unsat}, {n_unsolved_unsat})')
                else:
                    line_unsat.append(f'-')
                    
            # print(benchmark)
            
            print(benchmark_to_latex_runtime(benchmark))
            print('& \multirow{2}{*}{%s FNNs} &' % len(final_scores[benchmark]), ' & '.join(line_unsat) + ' \\\\')
            print('& &', ' & '.join(line_sat) + ' \\\\')
            print()
        else:
            print(benchmark_to_latex_runtime(benchmark))
            for net in final_scores[benchmark]:
                line_sat = []
                line_unsat = []
                for tool in TOOLS:
                    score_dict = final_scores[benchmark][net][tool]
                    # scores.append()
                    
                    runtime_sat = score_dict['runtime']['falsified']
                    runtime_unsat = score_dict['runtime']['verified']

                    n_solved_sat = score_dict['falsified']
                    n_solved_unsat = score_dict['verified']

                    n_unsolved_sat = INSTANCES_DETAIL_BY_BENCHMARK[benchmark][net]["sat"]  - n_solved_sat
                    n_unsolved_unsat = INSTANCES_DETAIL_BY_BENCHMARK[benchmark][net]["unsat"] - n_solved_unsat
                        
                    if runtime_sat > 0:
                        line_sat.append(f'{runtime_sat:.01f} ({n_solved_sat}, {n_unsolved_sat})')
                    else:
                        line_sat.append(f'-')
                    
                    if runtime_unsat > 0:
                        line_unsat.append(f'{runtime_unsat:.01f} ({n_solved_unsat}, {n_unsolved_unsat})')
                    else:
                        line_unsat.append(f'-')
                        
                print('& \multirow{2}{*}{%s} &' % network_to_latex(net.replace('_', '-')), ' & '.join(line_unsat) + ' \\\\')
                # print('\t', net, 'UNSAT:', ' & '.join(line_unsat) + ' \\\\')
                print('& &', ' & '.join(line_sat) + ' \\\\')
                # print('\t', net, 'SAT  :', ' & '.join(line_sat) + ' \\\\')
                print('\cmidrule(lr){2-8}')
                print()
                # exit()
            
    print('\\bottomrule')
            
            
# get_table_time(FINAL_SCORES)
get_table_ranking(FINAL_SCORES)