from script_tools.wmiexec import WMIEXEC


def put_file(src_file, des_path, des_ip, username, password, domain="", share="ADMIN$"):
    """upload file"""
    cmd_str = "put " + str(src_file) + " " + str(des_path)
    executor = WMIEXEC(cmd_str, username, password, domain, share=share)
    executor.run(des_ip)
    return {
        "result": True,
        "data": "upload {} success to {}:{}".format(src_file, des_ip, des_path),
    }


def execute_cmd(cmd_str, ipaddr, username, password, domain="", share="ADMIN$", noOutput=False):
    """execute command"""
    executor = WMIEXEC(cmd_str, username, password, domain, share=share, noOutput=noOutput)
    result_data = executor.run(ipaddr)
    return {"result": True, "data": result_data}
