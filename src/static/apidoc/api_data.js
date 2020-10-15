define({ "api": [
  {
    "type": "get",
    "url": "/ap/ap_is_using/",
    "title": "返回正在被使用的接入点",
    "name": "ap_is_using",
    "group": "Ap",
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "POST",
    "url": "/ap/",
    "title": "新增接入点",
    "name": "create_ap",
    "group": "Ap",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>接入点名称</p>"
          },
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "servers",
            "description": "<p>服务器列表</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "servers.inner_ip",
            "description": "<p>内网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "servers.outer_ip",
            "description": "<p>外网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "package_inner_url",
            "description": "<p>安装包内网地址</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "package_outer_url",
            "description": "<p>安装包外网地址</p>"
          },
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "zk_hosts",
            "description": "<p>ZK服务器</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "zk_hosts.zk_ip",
            "description": "<p>ZK IP地址</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "zk_hosts.port",
            "description": "<p>ZK端口</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "zk_account",
            "description": "<p>ZK账号</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "zk_password",
            "description": "<p>ZK密码</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "agent_config",
            "description": "<p>Agent配置信息</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "agent_config.linux",
            "description": "<p>Linux Agent配置信息</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.setup_path",
            "description": "<p>Linux Agent安装路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.data_path",
            "description": "<p>Linux Agent数据文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.run_path",
            "description": "<p>Linux Agent运行路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.log_path",
            "description": "<p>Linux Agent日志文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "agent_config.windows",
            "description": "<p>Windows配置信息</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.windows.setup_path",
            "description": "<p>Windows Agent安装路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.windows.data_path",
            "description": "<p>Windows Agent数据文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.windows.log_path",
            "description": "<p>Windows Agent日志文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "description",
            "description": "<p>描述</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求参数",
          "content": "{\n    \"name\": \"接入点名称\",\n    \"zk_hosts\": [\n        {\n            \"zk_ip\": \"127.0.0.1\",\n            \"zk_port: 111,\n        },\n        {\n            \"zk_ip\": \"127.0.0.2\",\n            \"zk_port: 222,\n        }\n    ]\n    \"zk_user\": \"username\",\n    \"zk_password\": \"zk_password\",\n    \"servers\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"btfileserver\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"dataserver\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"taskserver\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"package_inner_url\": \"http://127.0.0.1/download/\",\n    \"package_outer_url\": \"http://127.0.0.2/download/\",\n    \"agent_config\": {\n        \"linux\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"run_path\": \"/usr/local/gse/run\",\n            \"log_path\": \"/usr/local/gse/log\"\n        },\n        \"windows\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"log_path\": \"/usr/local/gse/log\"\n        }\n    },\n    \"description\": \"描述\"\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "DELETE",
    "url": "/ap/{{pk}}/",
    "title": "删除接入点",
    "name": "delete_ap",
    "group": "Ap",
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "POST",
    "url": "/ap/init_plugin/",
    "title": "初始化插件信息",
    "name": "init_plugin_data",
    "group": "Ap",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "ap_id",
            "description": "<p>接入点ID</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "GET",
    "url": "/ap/",
    "title": "查询接入点列表",
    "name": "list_ap",
    "group": "Ap",
    "success": {
      "examples": [
        {
          "title": "成功返回",
          "content": "[{\n    \"id\": 1,\n    \"name\": \"接入点名称\",\n    \"zk_hosts\": [\n        {\n            \"zk_ip\": \"127.0.0.1\",\n            \"zk_port: 111,\n        },\n        {\n            \"zk_ip\": \"127.0.0.2\",\n            \"zk_port: 222,\n        }\n    ]\n    \"zk_user\": \"username\",\n    \"zk_password\": \"zk_password\",\n    \"servers\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"package_inner_url\": \"http://127.0.0.1/download/\",\n    \"package_outer_url\": \"http://127.0.0.2/download/\",\n    \"agent_config\": {\n        \"linux\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"run_path\": \"/usr/local/gse/run\",\n            \"log_path\": \"/usr/local/gse/log\"\n        },\n        \"windows\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"log_path\": \"/usr/local/gse/log\"\n        }\n    },\n    \"description\": \"描述\"\n}]",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "GET",
    "url": "/ap/{{pk}}/",
    "title": "查询接入点详情",
    "name": "retrieve_ap",
    "group": "Ap",
    "success": {
      "examples": [
        {
          "title": "成功返回",
          "content": "{\n    \"id\": 1,\n    \"name\": \"接入点名称\",\n    \"zk_hosts\": [\n        {\n            \"zk_ip\": \"127.0.0.1\",\n            \"zk_port: 111,\n        },\n        {\n            \"zk_ip\": \"127.0.0.2\",\n            \"zk_port: 222,\n        }\n    ]\n    \"zk_user\": \"username\",\n    \"zk_password\": \"zk_password\",\n    \"servers\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"package_inner_url\": \"http://127.0.0.1/download/\",\n    \"package_outer_url\": \"http://127.0.0.2/download/\",\n    \"agent_config\": {\n        \"linux\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"run_path\": \"/usr/local/gse/run\",\n            \"log_path\": \"/usr/local/gse/log\"\n        },\n        \"windows\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"log_path\": \"/usr/local/gse/log\"\n        }\n    },\n    \"description\": \"描述\"\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "POST",
    "url": "/ap/test/",
    "title": "接入点可用性测试",
    "name": "test_ap",
    "group": "Ap",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "servers",
            "description": "<p>服务器列表</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "servers.inner_ip",
            "description": "<p>内网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "servers.outer_ip",
            "description": "<p>外网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "package_inner_url",
            "description": "<p>安装包内网地址</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "package_outer_url",
            "description": "<p>安装包外网地址</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求参数",
          "content": "{\n    \"servers\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"package_inner_url\": \"http://127.0.0.1/download/\",\n    \"package_outer_url\": \"http://127.0.0.2/download/\"\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"test_result\": false,\n    \"test_logs\": [\n      {\n        \"log_level\": \"INFO\",\n        \"log\": \"检测 127.0.0.1 连接正常\"\n      },\n      {\n        \"log_level\": \"ERROR\",\n        \"log\": \"检测 127.0.0.1 下载失败\"\n      }\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "PUT",
    "url": "/ap/{{pk}}/",
    "title": "编辑接入点",
    "name": "update_ap",
    "group": "Ap",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>接入点名称</p>"
          },
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "servers",
            "description": "<p>服务器列表</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "servers.inner_ip",
            "description": "<p>内网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "servers.outer_ip",
            "description": "<p>外网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "package_inner_url",
            "description": "<p>安装包内网地址</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "package_outer_url",
            "description": "<p>安装包外网地址</p>"
          },
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "zk_hosts",
            "description": "<p>ZK服务器</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "zk_hosts.zk_ip",
            "description": "<p>ZK IP地址</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "zk_hosts.port",
            "description": "<p>ZK端口</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "zk_account",
            "description": "<p>ZK账号</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "zk_password",
            "description": "<p>ZK密码</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "agent_config",
            "description": "<p>Agent配置信息</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "agent_config.linux",
            "description": "<p>Linux Agent配置信息</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.setup_path",
            "description": "<p>Linux Agent安装路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.data_path",
            "description": "<p>Linux Agent数据文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.run_path",
            "description": "<p>Linux Agent运行路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.linux.log_path",
            "description": "<p>Linux Agent日志文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "Object",
            "optional": false,
            "field": "agent_config.windows",
            "description": "<p>Windows配置信息</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.windows.setup_path",
            "description": "<p>Windows Agent安装路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.windows.data_path",
            "description": "<p>Windows Agent数据文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "agent_config.windows.log_path",
            "description": "<p>Windows Agent日志文件路径</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "description",
            "description": "<p>描述</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求参数",
          "content": "{\n    \"name\": \"接入点名称\",\n    \"servers\": [\n        {\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\"\n        }\n    ],\n    \"package_inner_url\": \"http://127.0.0.1/download/\",\n    \"package_outer_url\": \"http://127.0.0.2/download/\",\n    \"agent_config\": {\n        \"linux\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"run_path\": \"/usr/local/gse/run\",\n            \"log_path\": \"/usr/local/gse/log\"\n        },\n        \"windows\": {\n            \"setup_path\": \"/usr/local/gse\",\n            \"data_path\": \"/usr/local/gse/data\",\n            \"log_path\": \"/usr/local/gse/log\"\n        }\n    },\n    \"description\": \"描述\"\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/ap.py",
    "groupTitle": "Ap"
  },
  {
    "type": "POST",
    "url": "/cloud/",
    "title": "创建云区域",
    "name": "create_cloud",
    "group": "Cloud",
    "description": "<p>ap_id==-1代表自动选择</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "bk_cloud_name",
            "description": "<p>云区域名称</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "isp",
            "description": "<p>云服务商</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "ap_id",
            "description": "<p>接入点ID</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求参数",
          "content": "{\n    \"bk_cloud_name\": \"云区域名称\",\n    \"isp\": \"tencent\",\n    \"ap_id\": 1,\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"bk_cloud_id\": 1\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/cloud.py",
    "groupTitle": "Cloud"
  },
  {
    "type": "DELETE",
    "url": "/cloud/{{pk}}/",
    "title": "删除云区域",
    "name": "delete_cloud",
    "group": "Cloud",
    "version": "0.0.0",
    "filename": "apps/node_man/views/cloud.py",
    "groupTitle": "Cloud"
  },
  {
    "type": "GET",
    "url": "/cloud/",
    "title": "查询云区域列表",
    "name": "list_cloud",
    "group": "Cloud",
    "description": "<p>ap_id==-1代表自动选择接入点</p>",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"bk_cloud_id\": 1,\n        \"bk_cloud_name\": \"云区域名称\",\n        \"isp\": \"tencent\",\n        \"isp_name\": \"腾讯云\",\n        \"isp_icon\": \"base64\",\n        \"ap_id\": 1,\n        \"ap_name\": \"接入点名称\",\n        \"proxy_count\": 100,\n        \"node_count\": 200,\n        \"is_visible\": true\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/cloud.py",
    "groupTitle": "Cloud"
  },
  {
    "type": "GET",
    "url": "/cloud/{{pk}}/biz/",
    "title": "查询某主机服务信息",
    "name": "list_cloud_biz",
    "group": "Cloud",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"data\": [\n        53\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/cloud.py",
    "groupTitle": "Cloud"
  },
  {
    "type": "GET",
    "url": "/cloud/{{pk}}/",
    "title": "查询云区域详情",
    "name": "retrieve_cloud",
    "group": "Cloud",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"bk_cloud_id\": 1,\n    \"bk_cloud_name\": \"云区域名称\",\n    \"isp\": \"tencent\",\n    \"isp_name\": \"腾讯云\",\n    \"isp_icon\": \"\",\n    \"ap_id\": 1,\n    \"ap_name\": \"接入点名称\",\n    \"bk_biz_scope\": [1, 2, 3],\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/cloud.py",
    "groupTitle": "Cloud"
  },
  {
    "type": "PUT",
    "url": "/cloud/{{pk}}/",
    "title": "编辑云区域",
    "name": "update_cloud",
    "group": "Cloud",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "bk_cloud_name",
            "description": "<p>云区域名称</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "isp",
            "description": "<p>云服务商</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "ap_id",
            "description": "<p>接入点ID</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": false,
            "field": "bk_biz_scope",
            "description": "<p>业务范围</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求参数",
          "content": "{\n    \"bk_cloud_name\": \"云区域名称\",\n    \"isp\": \"tencent\",\n    \"ap_id\": 1,\n    \"bk_biz_scope\": [1, 2, 3]\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/cloud.py",
    "groupTitle": "Cloud"
  },
  {
    "type": "POST",
    "url": "/host/search/",
    "title": "查询主机列表",
    "name": "list_host",
    "group": "Host",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "bk_biz_id",
            "description": "<p>业务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "bk_host_id",
            "description": "<p>主机ID</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "condition",
            "description": "<p>搜索条件，支持os_type, ip, status <br> version, bk_cloud_id, node_from 和 模糊搜索query</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "exclude_hosts",
            "description": "<p>跨页全选排除主机</p>"
          },
          {
            "group": "Parameter",
            "type": "String[]",
            "optional": true,
            "field": "extra_data",
            "description": "<p>额外信息, 如 ['identity_info', 'job_result', 'topology']</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": true,
            "field": "page",
            "description": "<p>当前页数</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": true,
            "field": "pagesize",
            "description": "<p>分页大小</p>"
          },
          {
            "group": "Parameter",
            "type": "Boolean",
            "optional": true,
            "field": "only_ip",
            "description": "<p>只返回IP</p>"
          },
          {
            "group": "Parameter",
            "type": "Boolean",
            "optional": true,
            "field": "running_count",
            "description": "<p>返回正在运行机器数量</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"total\": 188,\n    \"list\": [\n        {\n            \"bk_cloud_id\": 1,\n            \"bk_cloud_name\": \"云区域名称\",\n            \"bk_biz_id\": 2,\n            \"bk_biz_name\": \"业务名称\",\n            \"bk_host_id\": 1,\n            \"os_type\": \"linux\",\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\",\n            \"login_ip\": \"127.0.0.3\",\n            \"data_ip\": \"127.0.0.4\",\n            \"status\": \"RUNNING\",\n            \"version\": \"1.1.0\",\n            \"ap_id\": -1,\n            \"identity_info\": {},\n            \"job_result\": {\n                \"job_id\": 1,\n                \"status\": \"FAILED\",\n                \"current_step\": \"下载安装包\",\n            }\n        }\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/host.py",
    "groupTitle": "Host"
  },
  {
    "type": "POST",
    "url": "/host/remove_host/",
    "title": "移除主机",
    "description": "<p>成功删除的host_id会在返回结果的success字段中。<br> 如果需要删除的host_id不存在在数据库中，则会出现在fail字段中。<br> 非跨页全选仅需传bk_host_id，跨页全选则不需要传bk_host_id。<br> 此外：<br> 如果is_proxy为true，则只针对Proxy做删除；<br> 如果is_proxy为false，则只针对AGENT和PAGENT做删除。<br> bk_host_id，exclude_hosts 必填一个。<br> 若填写了 exclude_hosts ，则代表跨页全选模式。<br> 注意, 云区域ID、业务ID等筛选条件，仅在跨页全选模式下有效。<br></p>",
    "name": "remove_host",
    "group": "Host",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "bk_host_id",
            "description": "<p>主机ID列表</p>"
          },
          {
            "group": "Parameter",
            "type": "Boolean",
            "optional": false,
            "field": "is_proxy",
            "description": "<p>是否针对Proxy的删除</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "bk_biz_id",
            "description": "<p>业务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "conditions",
            "description": "<p>搜索条件，支持os_type, ip, status <br> version, bk_cloud_id, node_from 和 模糊搜索query</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "exclude_hosts",
            "description": "<p>跨页全选排除主机</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"success\": [\n        6121\n    ],\n    \"fail\": []\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/host.py",
    "groupTitle": "Host"
  },
  {
    "type": "GET",
    "url": "/host/biz_proxies/",
    "title": "查询业务下云区域的proxy集合",
    "name": "retrieve_biz_proxies",
    "group": "Host",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "bk_biz_id",
            "description": "<p>业务ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[{\n    \"bk_cloud_id\": 1,\n    \"bk_host_id\": 1,\n    \"inner_ip\": \"127.0.0.1\",\n    \"outer_ip\": \"\",\n    \"login_ip\": null,\n    \"data_ip\": null,\n    \"bk_biz_id\": 1\n}]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/host.py",
    "groupTitle": "Host"
  },
  {
    "type": "GET",
    "url": "/host/proxies/",
    "title": "查询云区域的proxy列表",
    "name": "retrieve_cloud_proxies",
    "group": "Host",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "bk_cloud_id",
            "description": "<p>云区域ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[{\n    \"bk_cloud_id\": 1,\n    \"bk_host_id\": 1,\n    \"inner_ip\": \"127.0.0.1\",\n    \"outer_ip\": \"127.0.0.2\",\n    \"login_ip\": \"127.0.0.3\",\n    \"data_ip\": \"127.0.0.4\",\n    \"status\": \"RUNNING\",\n    \"version\": \"1.1.0\",\n\n    \"account\": \"root\",\n    \"auth_type\": \"PASSWORD\",\n    \"port\": 22,\n\n    \"ap_id\": 1,\n    \"ap_name\": \"接入点名称\"\n}]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/host.py",
    "groupTitle": "Host"
  },
  {
    "type": "POST",
    "url": "/host/update_single/",
    "title": "更新主机信息",
    "name": "update_host",
    "group": "Host",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "bk_host_id",
            "description": "<p>主机ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": true,
            "field": "bk_cloud_id",
            "description": "<p>云区域ID</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "inner_ip",
            "description": "<p>内网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "outer_ip",
            "description": "<p>外网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "login_ip",
            "description": "<p>登录IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "data_ip",
            "description": "<p>数据IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "account",
            "description": "<p>账户名</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": true,
            "field": "ap_id",
            "description": "<p>接入点ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": true,
            "field": "port",
            "description": "<p>端口</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "auth_type",
            "description": "<p>认证类型</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "password",
            "description": "<p>密码</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/host.py",
    "groupTitle": "Host"
  },
  {
    "type": "POST",
    "url": "/job/{{pk}}/collect_log/",
    "title": "查询日志",
    "name": "collect_job_log",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "job_id",
            "description": "<p>任务ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"celery_id\": \"c0072075-730b-461b-8c3e-1f00095b7348\"\n},",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "GET",
    "url": "/job/{{pk}}/get_job_commands/",
    "title": "获取安装命令",
    "name": "get_job_commands",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "job_id",
            "description": "<p>任务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "bk_host_id",
            "description": "<p>主机ID，-1时返回每个云区域的安装命令</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    bk_cloud_id: {\n        'win_commands': '',\n        'pre_commands': '',\n        'run_commands': ''\n    }\n},",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "GET",
    "url": "/job/{{pk}}/log/",
    "title": "查询日志",
    "name": "get_job_log",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "job_id",
            "description": "<p>任务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "instance_id",
            "description": "<p>实例ID</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "重装、升级等请求参数",
          "content": "{\n    \"bk_host_id\": 1\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"step\": \"检查网络连通性\",\n        \"status\": \"success\",\n        \"log\": \"checking network……\\nok\"\n    },\n    {\n        \"step\": \"检查用户\",\n        \"status\": \"success\",\n        \"log\": \"checking user……\\nusername is root\\nok\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "POST",
    "url": "/job/install/",
    "title": "安装类任务",
    "description": "<p>新安装Agent、新安装Proxy、重装、替换等操作</p>",
    "name": "install_job",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "job_type",
            "description": "<p>任务类型</p>"
          },
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "hosts",
            "description": "<p>主机信息</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "host.bk_cloud_id",
            "description": "<p>云区域ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": true,
            "field": "host.ap_id",
            "description": "<p>接入点ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": true,
            "field": "hosts.bk_host_id",
            "description": "<p>主机ID, 创建时可选, 更改时必选</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "allowedValues": [
              "\"Windows\"",
              "\"Linux\"",
              "\"AIX\""
            ],
            "optional": false,
            "field": "hosts.os_type",
            "description": "<p>操作系统类型</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "hosts.bk_biz_id",
            "description": "<p>业务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "hosts.inner_ip",
            "description": "<p>内网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "hosts.outer_ip",
            "description": "<p>外网IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "hosts.login_ip",
            "description": "<p>登录IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "hosts.data_ip",
            "description": "<p>数据IP</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "hosts.account",
            "description": "<p>账户名</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "hosts.port",
            "description": "<p>端口</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "hosts.auth_type",
            "description": "<p>认证类型</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "hosts.password",
            "description": "<p>密码</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "hosts.key",
            "description": "<p>密钥</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": true,
            "field": "hosts.retention",
            "description": "<p>密码保留天数</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": true,
            "field": "replace_host_id",
            "description": "<p>要替换的ProxyID，替换proxy时使用</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "安装请求参数",
          "content": "{\n    \"job_type\": \"INSTALL_AGENT\",\n    \"hosts\": [\n        {\n            \"bk_cloud_id\": 1,\n            \"ap_id\": 1,\n            \"bk_biz_id\": 2,\n            \"os_type\": \"Linux\",\n            \"inner_ip\": \"127.0.0.1\",\n            \"outer_ip\": \"127.0.0.2\",\n            \"login_ip\": \"127.0.0.3\",\n            \"data_ip\": \"127.0.0.4\",\n            \"account\": \"root\",\n            \"port\": 22,\n            \"auth_type\": \"PASSWORD\",\n            \"password\": \"password\",\n            \"key\": \"key\"\n        }\n    ],\n    \"retention\": 1,\n    \"replace_host_id\": 1\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"job_id\": 35,\n    \"ip_filter\": []\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "POST",
    "url": "/job/job_list/",
    "title": "查询任务列表",
    "name": "list_job",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "List",
            "optional": false,
            "field": "job_id",
            "description": "<p>任务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "job_type",
            "description": "<p>任务类型</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "status",
            "description": "<p>状态</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "created_by",
            "description": "<p>执行者</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "bk_biz_id",
            "description": "<p>业务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "page",
            "description": "<p>当前页数</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "pagesize",
            "description": "<p>分页大小</p>"
          },
          {
            "group": "Parameter",
            "type": "object",
            "optional": true,
            "field": "sort",
            "description": "<p>排序</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "allowedValues": [
              "[\"total_count\"",
              "\"failed_count\"",
              "\"success_count\"]"
            ],
            "optional": true,
            "field": "sort.head",
            "description": "<p>排序字段</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "allowedValues": [
              "[\"ASC\"",
              "\"DEC\"]"
            ],
            "optional": true,
            "field": "sort.sort_type",
            "description": "<p>排序类型</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求例子:",
          "content": "{\n    \"page\": 1,\n    \"pagesize\": 20,\n    \"job_type\": [\"INSTALL_AGENT\"]\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"total\": 100,\n    \"list\": [\n        {\n            \"id\": 1,\n            \"job_type\": \"INSTALL_PROXY\",\n            \"job_type_display\": \"安装Proxy\",\n            \"creator\": \"admin\",\n            \"start_time\": \"2019-10-08 11:10:10\",\n            \"cost_time\": 120,\n            \"status\": \"RUNNING\",\n            \"bk_biz_scope_display\": [\"蓝鲸\", \"layman\"]\n            \"statistics\": {\n                \"success_count\": 200,\n                \"failed_count\": 100,\n                \"running_count\": 100,\n                \"total_count\": 100\n            }\n        }\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "POST",
    "url": "/job/operate/",
    "title": "操作类任务",
    "description": "<p>用于只有bk_host_id参数的主机下线、重启等操作。<br> bk_host_id和exclude_hosts必填一个。<br> 若填写了 exclude_hosts ，则代表跨页全选模式。<br> 注意, 云区域ID、业务ID等筛选条件，仅在跨页全选模式下有效。<br></p>",
    "name": "operate_job",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "job_type",
            "description": "<p>任务类型</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "bk_biz_id",
            "description": "<p>业务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "conditions",
            "description": "<p>搜索条件，支持os_type, ip, status <br> version, bk_cloud_id, node_from 和 模糊搜索query</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "exclude_hosts",
            "description": "<p>跨页全选排除主机</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "bk_host_id",
            "description": "<p>主机ID 主机ID和跨页全选排除主机必选一个</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "安装请求参数",
          "content": "{\n    \"job_type\": \"RESTART_PROXY\",\n    \"bk_host_id\": [7731, 7732]\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "POST",
    "url": "/job/{{pk}}/details/",
    "title": "查询任务详情",
    "name": "retrieve_job",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "conditions",
            "description": "<p>条件</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "page",
            "description": "<p>当前页数</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "pagesize",
            "description": "<p>分页大小</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"total\": 100,\n    \"list\": [\n        {\n            \"bk_host_id\": 1,\n            \"inner_ip\": \"127.0.0.1\",\n            \"bk_cloud_id\": 1,\n            \"bk_cloud_name\": \"云区域名称\",\n            \"bk_biz_id\": 2,\n            \"bk_biz_name\": \"业务名称\",\n            \"status\": \"RUNNING\",\n            \"status_display\": \"正在执行\"\n        }\n    ],\n    \"statistics\": {\n        \"success_count\": 200,\n        \"failed_count\": 100,\n        \"running_count\": 100,\n        \"total_count\": 100\n    },\n    \"status\": \"RUNNING\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "POST",
    "url": "/job/{{pk}}/retry/",
    "title": "重试任务",
    "name": "retry_job",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number[]",
            "optional": false,
            "field": "instance_id_list",
            "description": "<p>主机ID列表</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "重装、升级等请求参数",
          "content": "{\n    \"instance_id_list\": [1, 2, 3]\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "POST",
    "url": "/job/{{pk}}/retry_node/",
    "title": "原子粒度重试任务",
    "name": "retry_node",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "instance_id",
            "description": "<p>实例id</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "重试时请求参数",
          "content": "{\n    \"instance_id\": host|instance|host|20.7.18.2-0-0\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"result\": true,\n    \"data\": {\n        \"retry_node_id\": \"6f48169ed1193574961757a57d03a778\",\n        \"retry_node_name\": \"安装\"\n    },\n    \"code\": 0,\n    \"message\": \"\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "POST",
    "url": "/job/{{pk}}/revoke/",
    "title": "终止任务",
    "name": "revoke_job",
    "group": "Job",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number[]",
            "optional": false,
            "field": "instance_id_list",
            "description": "<p>主机ID列表</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求样例",
          "content": "{\n    \"instance_id_list\": [1, 2, 3]\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/job.py",
    "groupTitle": "Job"
  },
  {
    "type": "GET",
    "url": "/meta/filter_condition/",
    "title": "获取过滤条件",
    "name": "get_filter_condition",
    "group": "Meta",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "category",
            "description": "<p>支持: host, job, plugin</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"name\": \"操作系统\",\n        \"id\": \"os_type\",\n        \"children\": [\n            {\n                \"name\": \"Linux\",\n                \"id\": \"Linux\"\n            },\n            {\n                \"name\": \"Windows\",\n                \"id\": \"Windows\"\n            }\n        ]\n    },\n    {\n        \"name\": \"Agent状态\",\n        \"id\": \"version\",\n        \"children\": [\n            {\n                \"name\": \"正常\",\n                \"id\": \"RUNNING\"\n            },\n            {\n                \"name\": \"未知\",\n                \"id\": \"UNKNOWN\"\n            }\n        ]\n    }\n]",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/meta.py",
    "groupTitle": "Meta"
  },
  {
    "type": "POST",
    "url": "/meta/job_settings/",
    "title": "任务配置接口",
    "name": "job_settings",
    "group": "Meta",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "install_p_agent_timeout",
            "description": "<p>安装P-Agent超时时间</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "install_agent_timeout",
            "description": "<p>安装Agent超时时间</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "install_proxy_timeout",
            "description": "<p>安装Proxy超时时间</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "install_download_limit_speed",
            "description": "<p>安装下载限速</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "parallel_install_number",
            "description": "<p>并行安装数</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "node_man_log_level",
            "description": "<p>节点管理日志级别</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/meta.py",
    "groupTitle": "Meta"
  },
  {
    "type": "GET",
    "url": "/meta/global_settings/",
    "title": "查询全局配置",
    "name": "retrieve_global_settings",
    "group": "Meta",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "allowedValues": [
              "\"isp\"",
              "\"job_settings\""
            ],
            "optional": false,
            "field": "key",
            "description": "<p>键值</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"isp\": \"tencent\",\n        \"isp_name\": \"腾讯云\",\n        \"isp_icon\": \"xxxx\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/meta.py",
    "groupTitle": "Meta"
  },
  {
    "type": "POST",
    "url": "/permission/fetch/",
    "title": "根据条件返回用户权限",
    "name": "fetch_permission",
    "group": "Permission",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "apply_info",
            "description": "<p>申请权限信息</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "allowedValues": [
              "\"cloud_edit\"",
              "\"cloud_delete\"",
              "\"cloud_view\"",
              "\"cloud_create\"",
              "\"ap_create\"",
              "\"ap_delete\"",
              "\"ap_edit\""
            ],
            "optional": false,
            "field": "apply_info.action",
            "description": "<p>操作类型</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "apply_info.instance_id",
            "description": "<p>实例ID</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "apply_info.instance_name",
            "description": "<p>实例名</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[{\n    \"system\": \"节点管理\",\n    \"action\": \"编辑云区域\",\n    \"instance_id\": 11,\n    \"instance_name\": cloud_one,\n    \"apply_url\": \"https://xxx.com/.../\"\n}]",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/permission.py",
    "groupTitle": "Permission"
  },
  {
    "type": "GET",
    "url": "/permission/ap/",
    "title": "返回用户接入点权限",
    "name": "list_ap_permission",
    "group": "Permission",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"edit_action\": [ap_ids],\n    \"delete_action\": [ap_ids],\n    \"create_action\": True or False\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/permission.py",
    "groupTitle": "Permission"
  },
  {
    "type": "GET",
    "url": "/permission/cloud/",
    "title": "返回用户云区域的权限",
    "name": "list_cloud_permission",
    "group": "Permission",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"edit_action\": [bk_cloud_ids],\n    \"delete_action\": [bk_cloud_ids],\n    \"create_action\": True or False,\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/permission.py",
    "groupTitle": "Permission"
  },
  {
    "type": "POST",
    "url": "/tjj/fetch_pwd/",
    "title": "查询支持铁将军的主机",
    "name": "fetch_pwd",
    "group": "Tjj",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String[]",
            "optional": false,
            "field": "hosts",
            "description": "<p>主机IP</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "请求参数",
          "content": "{\n    \"hosts\": [\n        \"x.x.x.x\",\n        \"x.x.x.x\"\n    ]\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"result\": True,\n    \"code\": 0,\n    \"data\": {\n        \"success_ips\": [\"x.x.x.x\", \"x.x.x.x\"],\n        \"failed_ips\": {\n            \"x.x.x.x\": {\n                \"Code\": 6,\n                \"Message\": \"x.x.x.x不存在\",\n                \"Password\": \"\"\n            }\n        }\n    },\n    \"message\": \"success\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/tjj.py",
    "groupTitle": "Tjj"
  },
  {
    "type": "POST",
    "url": "/plugin/create_export_task/",
    "title": "触发插件打包导出",
    "name": "create_export_plugin_task",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/create_config_template/",
    "title": "创建配置模板",
    "name": "create_plugin_config_template",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/create_register_task/",
    "title": "创建注册任务",
    "name": "create_register_task",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/delete/",
    "title": "删除插件",
    "name": "delete_plugin",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/export/download/",
    "title": "下载导出的内容,此处不做实际的文件读取，将由nginx负责处理",
    "name": "download_content",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/query_debug/",
    "title": "查询调试结果",
    "name": "query_debug",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/query_export_task/",
    "title": "获取一个导出任务结果",
    "name": "query_export_plugin_task",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/query_config_instance/",
    "title": "查询配置模板实例",
    "name": "query_plugin_config_instance",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/query_config_template/",
    "title": "查询配置模板",
    "name": "query_plugin_config_template",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/info/",
    "title": "查询插件信息",
    "name": "query_plugin_info",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/query_register_task/",
    "title": "查询插件注册任务",
    "name": "query_register_task",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/release/",
    "title": "发布插件",
    "name": "release_plugin",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/release_config_template/",
    "title": "发布配置模板",
    "name": "release_plugin_config_template",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/render_config_template/",
    "title": "渲染配置模板",
    "name": "render_plugin_config_template",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/start_debug/",
    "title": "开始调试",
    "name": "start_debug",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/stop_debug/",
    "title": "停止调试",
    "name": "stop_debug",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "POST",
    "url": "/package/upload/",
    "title": "上传文件接口",
    "name": "upload_file",
    "group": "backend_plugin",
    "version": "0.0.0",
    "filename": "apps/backend/plugin/views.py",
    "groupTitle": "backend_plugin"
  },
  {
    "type": "GET",
    "url": "/choice/category/",
    "title": "查询类别列表",
    "name": "list_category",
    "group": "choice",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": " [\n    {\n        \"id\": \"official\",\n        \"name\": \"官方插件\"\n    },\n    {\n        \"id\": \"external\",\n        \"name\": \"第三方插件\"\n    },\n    {\n        \"id\": \"scripts\",\n        \"name\": \"脚本插件\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/choice.py",
    "groupTitle": "choice"
  },
  {
    "type": "GET",
    "url": "/choice/job_type/",
    "title": "查询任务类型列表",
    "name": "list_job_type",
    "group": "choice",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": " [\n    {\n        \"id\": \"INSTALL_PROXY\",\n        \"name\": \"安装 ProxyPROXY\"\n    },\n    {\n        \"id\": \"INSTALL_AGENT\",\n        \"name\": \"安装 AgentAGENT\"\n    },\n    {\n        \"id\": \"RESTART_PROXY\",\n        \"name\": \"重启 ProxyPROXY\"\n    },\n    ... ...\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/choice.py",
    "groupTitle": "choice"
  },
  {
    "type": "GET",
    "url": "/choice/op/",
    "title": "查询操作列表",
    "name": "list_op",
    "group": "choice",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"id\": \"START\",\n        \"name\": \"启动\"\n    },\n    {\n        \"id\": \"STOP\",\n        \"name\": \"停止\"\n    },\n    ... ...\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/choice.py",
    "groupTitle": "choice"
  },
  {
    "type": "GET",
    "url": "/choice/os_type/",
    "title": "查询系统列表",
    "name": "list_os_type",
    "group": "choice",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"id\": \"LINUX\",\n        \"name\": \"LINUX\"\n    },\n    {\n        \"id\": \"WINDOWS\",\n        \"name\": \"WINDOWS\"\n    },\n    {\n        \"id\": \"AIX\",\n        \"name\": \"AIX\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/choice.py",
    "groupTitle": "choice"
  },
  {
    "type": "GET",
    "url": "/cmdb/fetch_topo/",
    "title": "获得拓扑信息",
    "name": "fetch_topo",
    "group": "cmdb",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int",
            "optional": false,
            "field": "bk_biz_id",
            "description": "<p>主机ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[{\n    \"bk_set_name\": \"空闲机池\",\n    \"bk_set_id\": 2,\n    \"modules\": [\n        {\n            \"bk_module_name\": \"空闲机\",\n            \"bk_module_id\": 3\n        },\n        {\n            \"bk_module_name\": \"故障机\",\n            \"bk_module_id\": 4\n        }\n    ]\n}]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/cmdb.py",
    "groupTitle": "cmdb"
  },
  {
    "type": "GET",
    "url": "/cmdb/biz/",
    "title": "查询用户所有业务",
    "name": "retrieve_biz",
    "group": "cmdb",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "allowedValues": [
              "\"agent_view\"",
              "\"agent_operate\"",
              "\"proxy_operate\"",
              "\"plugin_view\"",
              "\"plugin_operate\"",
              "\"task_history_view\""
            ],
            "optional": false,
            "field": "action",
            "description": "<p>操作类型</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[{\n    \"bk_biz_id\": \"50\",\n    \"bk_biz_name\": \"蓝鲸XX\"\n}]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/cmdb.py",
    "groupTitle": "cmdb"
  },
  {
    "type": "GET",
    "url": "/debug/fetch_hosts_by_subscription/",
    "title": "查询订阅任务下的主机",
    "name": "fetch_hosts_by_subscription",
    "group": "debug",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "int",
            "optional": false,
            "field": "subscription_id",
            "description": "<p>订阅任务ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"total\": 2,\n    \"list\": [\n        {\n            \"bk_host_id\": 9640,\n            \"bk_biz_id\": 6,\n            \"bk_cloud_id\": 0,\n            \"inner_ip\": \"10.123.8.74\",\n            \"os_type\": \"LINUX\",\n            \"node_type\": \"AGENT\",\n            \"plugin_status\": [\n                {\n                    \"name\": \"gseagent\",\n                    \"status\": \"UNKNOWN\",\n                    \"version\": \"\"\n                },\n                {\n                    \"name\": \"basereport\",\n                    \"status\": \"UNKNOWN\",\n                    \"version\": \"\"\n                },\n                {\n                    \"name\": \"bkmetricbeat\",\n                    \"status\": \"UNREGISTER\",\n                    \"version\": \"\"\n                },\n                ... ...\n            ]\n        },\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/debug.py",
    "groupTitle": "debug"
  },
  {
    "type": "GET",
    "url": "/debug/fetch_subscription_details/",
    "title": "查询订阅任务详情",
    "name": "fetch_subscription_details",
    "group": "debug",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "int",
            "optional": false,
            "field": "subscription_id",
            "description": "<p>订阅任务ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"task_id\": 497,\n        \"task_scope\": {\n            \"nodes\": [\n                {\n                    \"bk_host_id\": 9640\n                }\n            ],\n            \"bk_biz_id\": null,\n            \"node_type\": \"INSTANCE\",\n            \"object_type\": \"HOST\",\n            \"need_register\": false\n        },\n        \"task_actions\": {\n            \"host|instance|host|9640\": {\n                \"agent\": \"REINSTALL_AGENT\"\n            }\n        },\n        \"is_auto_trigger\": false,\n        \"create_time\": \"2020-07-29 16:35:41+0800\",\n        \"details\": \"https://paasee-dev.oa.com/o/bk_nodeman/api/debug/\n                    get_task_detail?subscription_id=362&task_id=497\"\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/debug.py",
    "groupTitle": "debug"
  },
  {
    "type": "GET",
    "url": "/debug/fetch_subscriptions_by_host/",
    "title": "查询主机涉及到的所有订阅任务",
    "name": "fetch_subscriptions_by_host",
    "group": "debug",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "int",
            "optional": false,
            "field": "bk_host_id",
            "description": "<p>主机ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    364,\n    365\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/debug.py",
    "groupTitle": "debug"
  },
  {
    "type": "GET",
    "url": "/debug/fetch_task_details/",
    "title": "查询任务执行详情",
    "name": "fetch_task_details",
    "group": "debug",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "int",
            "optional": false,
            "field": "subscription_id",
            "description": "<p>订阅任务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "int",
            "optional": false,
            "field": "task_id",
            "description": "<p>任务ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n    {\n        \"subscription_id\": 16,\n        \"task_id\": 26,\n        \"instance_id\": \"host|instance|host|1024\",\n        \"logs\": [\n            {\n                \"step\": \"选择接入点\",\n                \"status\": \"SUCCESS\",\n                \"log\": \"[2020-03-28 18:10:38 INFO] 开始选择接入点\\n[2020-03-28 18:10:38 INFO] 当前主机已分配接入点[默认接入点]\",\n                \"start_time\": \"2020-03-28 10:10:38\",\n                \"finish_time\": \"2020-03-28 10:10:38\"\n            },\n            {\n                \"step\": \"安装\",\n                \"status\": \"FAILED\",\n                \"log\": \"\",\n                \"start_time\": \"2020-03-28 10:10:38\",\n                \"finish_time\": \"2020-03-28 10:11:25\"\n            },\n            {\n                \"step\": \"查询Agent状态\",\n                \"status\": \"PENDING\",\n                \"log\": \"\",\n                \"start_time\": null,\n                \"finish_time\": null\n            },\n            {\n                \"step\": \"更新任务状态\",\n                \"status\": \"PENDING\",\n                \"log\": \"\",\n                \"start_time\": null,\n                \"finish_time\": null\n            }\n        ],\n        \"create_time\": \"2020-03-28 18:10:36+0800\",\n        \"update_time\": \"2020-03-28 18:10:36+0800\",\n        \"is_latest\": true\n    }\n]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/debug.py",
    "groupTitle": "debug"
  },
  {
    "type": "POST",
    "url": "/plugin/search/",
    "title": "查询插件列表",
    "name": "list_host",
    "group": "plugin",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "bk_biz_id",
            "description": "<p>业务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "bk_host_id",
            "description": "<p>主机ID</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "conditions",
            "description": "<p>搜索条件，支持os_type, ip, status <br> version, bk_cloud_id, node_from 和 模糊搜索query</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "exclude_hosts",
            "description": "<p>跨页全选排除主机</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": true,
            "field": "page",
            "description": "<p>当前页数</p>"
          },
          {
            "group": "Parameter",
            "type": "Int",
            "optional": true,
            "field": "pagesize",
            "description": "<p>分页大小</p>"
          },
          {
            "group": "Parameter",
            "type": "Boolean",
            "optional": true,
            "field": "only_ip",
            "description": "<p>只返回IP</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"total\": 188,\n    \"list\": [\n        {\n            \"bk_cloud_id\": 1,\n            \"bk_cloud_name\": \"云区域名称\",\n            \"bk_biz_id\": 2,\n            \"bk_biz_name\": \"业务名称\",\n            \"bk_host_id\": 1,\n            \"os_type\": \"linux\",\n            \"inner_ip\": \"127.0.0.1\",\n            \"plugin_status\": {}\n            \"job_result\": {\n                \"job_id\": 1,\n                \"status\": \"FAILED\",\n                \"current_step\": \"下载安装包\",\n            }\n        }\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/plugin.py",
    "groupTitle": "plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/{{pk}}/package/",
    "title": "查询进程包列表,pk为具体进程名",
    "name": "list_package",
    "group": "plugin",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "os",
            "description": "<p>系统类型</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[\n        {\n            \"id\":2,\n            \"pkg_name\":\"basereport-10.1.12.tgz\",\n            \"version\":\"10.1.12\",\n            \"module\":\"gse_plugin\",\n            \"project\":\"basereport\",\n            \"pkg_size\":4561957,\n            \"pkg_path\":\"/data/bkee/miniweb/download/linux/x86_64\",\n            \"md5\":\"046779753b6709635db0c861a1b0020e\",\n            \"pkg_mtime\":\"2019-11-01 20:46:52.404139\",\n            \"pkg_ctime\":\"2019-11-01 20:46:52.404139\",\n            \"location\":\"http://x.x.x.x/download/linux/x86_64\",\n            \"os\":\"linux\",\n            \"cpu_arch\":\"x86_64\"\n        },\n        {\n            \"id\":1,\n            \"pkg_name\":\"basereport-10.1.9.tgz\",\n            \"version\":\"10.1.9\",\n            \"module\":\"gse_plugin\",\n            \"project\":\"basereport\",\n            \"pkg_size\":4562217,\n            \"pkg_path\":\"/data/bkee/miniweb/download/linux/x86_64\",\n            \"md5\":\"6fe084f450352b1fa598a41a72800bc8\",\n            \"pkg_mtime\":\"2019-08-26 19:17:56.905309\",\n            \"pkg_ctime\":\"2019-08-26 19:17:56.905309\",\n            \"location\":\"http://x.x.x.x/download/linux/x86_64\",\n            \"os\":\"linux\",\n            \"cpu_arch\":\"x86_64\"\n        }\n    ]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/plugin.py",
    "groupTitle": "plugin"
  },
  {
    "type": "GET",
    "url": "/plugin/{{pk}}/process/",
    "title": "查询插件列表,pk为official, external 或 scripts",
    "name": "list_process",
    "group": "plugin",
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "[{\n    \"id\":14,\n    \"name\":\"bklogbeat\",\n    \"description\":\"windows日志文件采集\",\n    \"description_en\":\"Windows log collector\",\n    \"scenario\":\"数据平台，蓝鲸监控，日志检索等和日志相关的数据. 首次使用插件管理进行操作前，先到日志检索/数据平台等进行设置插件的功能项\",\n    \"scenario_en\":\"Log collection on data, bkmonitor, log-search apps\",\n    \"category\":\"official\",\n    \"config_file\":\"bklogbeat.conf\",\n    \"config_format\":\"yaml\",\n    \"use_db\":false,\n    \"is_binary\":true,\n    \"auto_launch\":false\n}]",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/plugin.py",
    "groupTitle": "plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/process/status/",
    "title": "查询主机进程状态信息",
    "name": "list_process_status",
    "group": "plugin",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": false,
            "field": "bk_host_ids",
            "description": "<p>主机ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "请求示例:",
          "content": "{\n    \"bk_host_ids\": [1,2]\n}",
          "type": "json"
        },
        {
          "title": "成功返回:",
          "content": "{\n    \"result\": true,\n    \"code\": 0,\n    \"message\": \"\"\n    \"data\": [\n        {\n            \"bk_host_id\": 1,\n            \"name\": \"gseagent\",\n            \"status\": \"RUNNING\",\n            \"version\": \"1.60.54\"\n        },\n        {\n            \"bk_host_id\": 2,\n            \"name\": \"gseagent\",\n            \"status\": \"RUNNING\",\n            \"version\": \"1.60.54\"\n        }\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/plugin.py",
    "groupTitle": "plugin"
  },
  {
    "type": "POST",
    "url": "/plugin/operate/",
    "title": "插件操作类任务",
    "description": "<p>用于插件的各类操作。<br> bk_host_id和exclude_hosts必填一个。<br> 若填写了 exclude_hosts ，则代表跨页全选模式。<br> 注意, 云区域ID、业务ID等筛选条件，仅在跨页全选模式下有效。<br></p>",
    "name": "operate_plugin",
    "group": "plugin",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "job_type",
            "description": "<p>任务类型</p>"
          },
          {
            "group": "Parameter",
            "type": "Object[]",
            "optional": false,
            "field": "plugin_params",
            "description": "<p>插件信息</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "plugin_params.name",
            "description": "<p>插件名称</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "plugin_params.version",
            "description": "<p>插件版本</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "plugin_params.keep_config",
            "description": "<p>插件版本</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "plugin_params.no_restart",
            "description": "<p>插件版本</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": true,
            "field": "bk_biz_id",
            "description": "<p>业务ID</p>"
          },
          {
            "group": "Parameter",
            "type": "List",
            "optional": true,
            "field": "condition",
            "description": "<p>搜索条件，支持os_type, ip, status <br> version, bk_cloud_id, node_from 和 模糊搜索query</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "exclude_hosts",
            "description": "<p>跨页全选排除主机</p>"
          },
          {
            "group": "Parameter",
            "type": "Int[]",
            "optional": true,
            "field": "bk_host_id",
            "description": "<p>主机ID 主机ID和跨页全选排除主机必选一个</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "安装请求参数",
          "content": "{\n    \"job_type\": \"START_PLUGIN\",\n    \"bk_host_id\": [7731, 7732],\n    \"plugin_params\": {\n        \"name\": \"basereport\",\n        \"version\": \"10.1.12\"\n    }\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/node_man/views/plugin.py",
    "groupTitle": "plugin"
  },
  {
    "type": "POST",
    "url": "/subscription/cmdb_subscription/",
    "title": "接收cmdb事件回调",
    "name": "cmdb_subscription",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/collect_task_result_detail/",
    "title": "采集任务执行详细结果",
    "name": "collect_subscription_task_result_detail",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/create/",
    "title": "创建订阅",
    "name": "create_subscription",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/delete/",
    "title": "删除订阅",
    "name": "delete_subscription",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/fetch_commands/",
    "title": "返回安装命令",
    "name": "fetch_commands",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/get_gse_config/",
    "title": "获取配置",
    "name": "get_gse_config",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/instance_status/",
    "title": "查询订阅运行状态",
    "name": "query_instance_status",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/report_log/",
    "title": "上报日志",
    "name": "report_log",
    "group": "subscription",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "object",
            "optional": false,
            "field": "request",
            "description": ""
          }
        ]
      },
      "examples": [
        {
          "title": "请求参数",
          "content": "{\n    \"task_id\": \"node_id\",\n    \"token\": \"\",\n    \"logs\": [\n        {\n            \"timestamp\": \"1580870937\",\n            \"level\": \"INFO\",\n            \"step\": \"check_deploy_result\",\n            \"log\": \"gse agent has been deployed successfully\",\n            \"status\": \"DONE\"\n        }\n    ]\n}",
          "type": "Json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/backend/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/retry_node/",
    "title": "重试原子",
    "name": "retry_node",
    "group": "subscription",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "instance_id",
            "description": "<p>实例id</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "subscription_id",
            "description": "<p>订阅id</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "重试时请求参数",
          "content": "{\n    \"instance_id\": host|instance|host|20.7.18.2-0-0\n    \"subscription_id\": 123\n}",
          "type": "Json"
        }
      ]
    },
    "success": {
      "examples": [
        {
          "title": "成功返回:",
          "content": "{\n    \"retry_node_id\": \"6f48169ed1193574961757a57d03a778\",\n    \"retry_node_name\": \"安装\"\n}",
          "type": "json"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/retry/",
    "title": "重试失败的任务",
    "name": "retry_subscription",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/revoke/",
    "title": "终止正在执行的任务",
    "name": "revoke_subscription",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/run/",
    "title": "执行订阅",
    "name": "run_subscription",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/info/",
    "title": "订阅详情",
    "name": "subscription_info",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/switch/",
    "title": "订阅启停",
    "name": "subscription_switch",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/task_result/",
    "title": "任务执行结果",
    "name": "subscription_task_result",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/task_result_detail/",
    "title": "任务执行详细结果",
    "name": "subscription_task_result_detail",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  },
  {
    "type": "POST",
    "url": "/subscription/update/",
    "title": "更新订阅",
    "name": "update_subscription",
    "group": "subscription",
    "version": "0.0.0",
    "filename": "apps/backend/subscription/views.py",
    "groupTitle": "subscription"
  }
] });
