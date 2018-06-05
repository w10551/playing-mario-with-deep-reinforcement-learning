DeepQAgent(
    env=<FrameStackEnv<PenalizeDeathEnv<DownsampleEnv<MaxFrameskipEnv<RewardCacheEnv<TimeLimit<TetrisEnv<Tetris-v0>>>>>>>>,
    render_mode='rgb_array'
    replay_memory_size=750000,
    discount_factor=0.99,
    update_frequency=4,
    optimizer=<keras.optimizers.Adam object at 0x7ff3edd77278>,
    exploration_rate=AnnealingVariable(initial_value=1.0, final_value=0.1, steps=1000000),
    loss=huber_loss,
    target_update_freq=10000,
    dueling_network=True
)