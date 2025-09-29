import argparse
import sys, os
from ..core.simulator import main as run_simulation


def parse_args():
    p = argparse.ArgumentParser(description="Run SPP simulations")
    p.add_argument("--input_txt", type=str, required=True)
    p.add_argument("--one_indexed", action="store_true")
    p.add_argument("--attack", nargs=2, default=["random", "random"],
                   choices=["random", "hub", "closeness", "betweenness"])
    p.add_argument("--iter", type=int, default=1000)
    p.add_argument("--num_instance", type=int, default=1)
    p.add_argument("--output_dir", type=str, default="./spp_general/spp-general-notebook/data_simulator")
    p.add_argument("--C_values", nargs="+", default=None)  # aceita 'N'
    p.add_argument("--N_values", nargs="+", type=int, default=[300, 500, 600, 1000])
    p.add_argument("--rank_1", type=int, default=1)
    p.add_argument("--rank_2", type=int, default=2)
    return p.parse_args()

def main():
    args = parse_args()
    run_simulation(                        
        N_values=args.N_values,
        C_values=args.C_values,
        num_iter=args.iter,
        num_instance=args.num_instance,
        output_dir=args.output_dir,
        input_txt=args.input_txt,
        one_indexed=args.one_indexed,
        attack_mode_1=args.attack[0],
        attack_mode_2=args.attack[1],
        rank_1=args.rank_1,
        rank_2=args.rank_2,
    )

if __name__ == "__main__":
    main()
