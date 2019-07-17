## ML 

- `ml/write_dataset_config.py`
    - additional argument : `--training-z-estimation-method` for switching between the Z estimation method between `emb` (embedding) and `mc` (MonteCarlo)
    - the hardcoded options for each channel is removed and replaced by a logic
        - `estimationMethodAndClassMapGenerator()` simultaneously builds up the mapping of the classes and a list of estimation methods (from the given era), depending on `channel`, `training-z-estimation-method`
        - channel objects from `shape_producer.channel` are loaded into a dict and selected according to channel and era
        - logic for selecting different QCD sideband cuts for "tt"
    - fixed multiple bugs, especially in 2016 and tt
- `ml/create_training_dataset.sh`
    - passes new option `--training-z-estimation-method` to `ml/write_dataset_config.py`, emb is now default


- `ml/sum_training_weights.py`
    - channels read from dataset_config_file
    - new argument `--write-weights` (bool): if true, writes new inverse class weight to `ml/$era_$channel_training.yaml`
- `ml/sum_training_weights.sh`
    - now takes the `dataset_config_file` instead of the channels
    - now takes a channel as second argument. If none is given, the script is iterated over all channels.
    - default setting: orders `sum_training_weights.py` do overwrite the class weights with the ones generated from `combined_training_dataset.root`
    - uses `utils/multirun.sh` to run 



