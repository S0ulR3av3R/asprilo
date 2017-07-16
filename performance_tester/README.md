# ASPLog

## Description
    TODO

## Readme
### Run: 
    python logistics.py <parameter> <option> 

### Parameters and Options:
    -h,	--help		  	 Help
    -e,	--encoding <encoding_file>  Encoding file (default: encoding/encoding.lp)
    -i,	--instance <instance_file>  Instance file
    -s,	--solver <solver>           solver: {external | ground} (default: ground)
    -p,	--performance <Test dir>    directory with instances for performance tests (recursive)

### examples:

    python logistics.py -i instances/x4_y4_n16_r2_s3_ps1_pr2_u4_o2_N4.lp

    python logistics.py -i instances/x4_y4_n16_r2_s3_ps1_pr2_u4_o2_N4.lp -s external
    
    python logistics.py -p instances/


