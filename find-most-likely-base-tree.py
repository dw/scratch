
# Search some other Git repo for a commit containing a tree that most resembles
# the tree for the named commit from the repo in the CWD.

import subprocess


def get_hash_set(cwd, spec):
    output = subprocess.check_output(['git', 'ls-tree', '-r', spec], cwd=cwd)
    return set(line.split(None, 3)[2] for line in output.splitlines())


def get_rev_list(cwd, spec):
    output = subprocess.check_output(['git', 'rev-list', spec], cwd=cwd)
    return [s.strip() for s in output.splitlines()]



goal = get_hash_set('.', '7f18e42eb0423e27b431624f29d5d93af153c85f')
best_score = 1
best = None

cand_dir = '/home/dmw/linux-stable'
candidate_revs = get_rev_list(cand_dir, 'v3.0..v3.0.37')
for rev in candidate_revs:
    cand = get_hash_set(cand_dir, rev)
    score = len(goal & cand)
    print 'Trying', rev, '(%d hashes, %d common, %s best aka %.4f%%)' %\
        (len(cand), score, best_score, 100*((best_score)/len(goal)))
    if score > best_score:
        print 'Better candidate:', rev, '(%d common)' % (score,)
        best = rev
        best_score = float(score)

print
print 'Best candidate:', best
print 'Best common:', best_score
