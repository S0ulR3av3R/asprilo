# ASPLog

## Description
    TODO

## Readme
### Run: 
    python performace_tester.py <parameter> <option> 

### Parameters and Options:
    -h,	--help		  	 Help
    -e,	--encoding <encoding_file>  Encoding file (default: encoding/encoding.lp)
    -i,	--instance <instance_file>  Instance file
    -s,	--solver <solver>           solver: {external | ground} (default: ground)
    -p,	--performance <Test dir>    directory with instances for performance tests (recursive)

### examples:

    python performace_tester.py -i instances/x4_y4_n16_r2_s3_ps1_pr2_u4_o2_N4.lp

    python performace_tester.py -i instances/x4_y4_n16_r2_s3_ps1_pr2_u4_o2_N4.lp -s external
    
    python performace_tester.py -p instances/


