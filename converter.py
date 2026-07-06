import argparse
import nihonium as nh

def argparse_namespace_to_nh_run_config(args: argparse.Namespace):
    return nh.config.RunConfig(file=args.program, shell=args.shell,
                               pretty_print_ast=args.pretty_print_ast, debug=args.debug, vm=args.vm,
                               disable_default_natives=args.disable_default_natives,
                               natives=args.natives)