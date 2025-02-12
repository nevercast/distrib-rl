import os,sys
import random
random.seed(0)
import numpy as np
np.random.seed(0)
import torch
torch.manual_seed(0)

from PolicyOptimization.DistribPolicyGradients import Server
from Experiments import ExperimentManager
import traceback

def main():
    if len(sys.argv) == 1:
        experiment_path = "resources/experiments/test_experiments/walker2d_config.json"
    if len(sys.argv) == 2:
        experiment_path = sys.argv[1]
        if not os.path.exists(experiment_path):
            raise FileNotFoundError(f"No experiment file found at location '{experiment_path}'")

    server = Server()
    experiment_manager = ExperimentManager(server)
    experiment_manager.load_experiment(experiment_path)

    try:
        experiment_manager.run_experiments()
    except:
        print("\nFAILURE IN SERVER!\n")
        print(traceback.format_exc())
    finally:
        try:
            print("\nATTEMPTING TO SET REDIS TO STOPPING STATUS")
            server.cleanup()
        except:
            print("\n!!!CRITICAL FAILURE!!!\nUNABLE TO SET REDIS STATE TO STOPPING AFTER EXCEPTION IN CLIENT\n")
            print(traceback.format_exc())

if __name__ == "__main__":
    main()
