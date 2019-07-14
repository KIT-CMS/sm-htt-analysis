## utils:
`utils/multirun.sh`
:    - takes two arguments from the list and passes them to `run_procedure`
    - if PARALLEL is set two 1, the a given function is executed with a given argument list,
    - otherwise the programs are executed sequentially
    - usage:
```
function run_procedure() {
    ...
}
PARALLEL=1
source utils/multirun.sh
genArgsAndRun run_procedure 2016,2017 tt,mt
```


`utils/inlinediff.py`
:    - Assuming you have two files with similar output, but different values, inlinediff can show the differences - now with COLORS!
```
╰─ cat emb-stxs_stage0-inclusive.txt mc-stxs_stage0-inclusive.txt
> --- MultiDimFit ---
>best fit parameter values and profile-likelihood uncertainties:
>   r :    +1.000   -0.406/+0.462 (68%)
> --- MultiDimFit ---
>best fit parameter values and profile-likelihood uncertainties:
>   r :    +1.000   -0.415/+0.470 (68%)
╰─ ./utils/inlinediff.py emb-stxs_stage0-inclusive.txt mc-stxs_stage0-inclusive.txt
> --- MultiDimFit ---
>best fit parameter values and profile-likelihood uncertainties:
>   r :    +1.000   -0.4{06|15}/+0.4{62|70} (68%)
```

`utils/bashFunctionCollection.sh`
:   Provides the following functions:
    - `getPar $file $par`: tries to extract a value set in a bash|python file via a regex
    - `overridePar $file $par $val`: tries to override a value set in a bash|python file via a regex
    - `recommendCPUs`: *recommends* a number of cpus to use with formula (1-averageCpuLoad)*0.7 
    - `loginfo`, `logwarn`, `logerror` Colored output with timestamp for instance:
```
╰─ logwarn foo                                         
[WARN] 19-07-09 16:34: foo
```



