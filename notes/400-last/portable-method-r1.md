# Portable verification receipt

The documented first shell block was extracted without changes from
`docs/requests/400-penalty-free-kick.md` at `c9d8adb4` into
`/tmp/T90-portable-recipe.sh`.

`portable-verification-r1.log` records the first execution in the collector
checkout (existing cache; pass). It is not the clean-cache check.

`portable-clean-verification-r1.log` records the same block executed by
`bash -e /tmp/T90-portable-recipe.sh` in `/tmp/T90-portable-check`, populated only
by `git archive c9d8adb4 | tar -x` before execution. All four archives were
downloaded there and extracted by the recipe. The environment supplied
`GIT_DIR=/home/diego/projects/goal2-archaeology/.git` solely because a Git archive
has no commit database for the verifier's recorded collector `git show` checks.
A normal source clone already has that database. No collector cache or machine
input was copied into the clean tree. The final line reports PASS, including all
942 observations and four private download hashes. No guest was executed.
