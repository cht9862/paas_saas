(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[3],{261:function(t,e,r){"use strict";r.r(e);var i=r(552);var a=r(388);for(var n in a)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return a[t]}))})(n);var s=r(516);var o=r(2);var u=Object(o["a"])(a["default"],i["a"],i["b"],false,null,null,null);e["default"]=u.exports},388:function(t,e,r){"use strict";r.r(e);var i=r(389);var a=r.n(i);for(var n in i)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return i[t]}))})(n);e["default"]=a.a},389:function(t,e,r){"use strict";var i=r(1);Object.defineProperty(e,"__esModule",{value:true});e.default=void 0;var a=i(r(5));var n=i(r(6));var s=i(r(17));var o=r(9);var u=i(r(510));var l=i(r(514));var c=r(10);function d(t,e){var r=Object.keys(t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);if(e)i=i.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}));r.push.apply(r,i)}return r}function p(t){for(var e=1;e<arguments.length;e++){var r=arguments[e]!=null?arguments[e]:{};if(e%2){d(Object(r),true).forEach((function(e){(0,s.default)(t,e,r[e])}))}else if(Object.getOwnPropertyDescriptors){Object.defineProperties(t,Object.getOwnPropertyDescriptors(r))}else{d(Object(r)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}}return t}var f={name:"AccessPoint",components:{StepHost:u.default,StepInfo:l.default},props:{pointId:{type:String,default:""}},data:function t(){return{curStep:1,stepCheck:false}},computed:p(p({},(0,o.mapGetters)("config",["detail","loading"])),{},{isEdit:function t(){return!(0,c.isEmpty)(this.pointId)}}),mounted:function t(){var e=this;return(0,n.default)(a.default.mark((function t(){return a.default.wrap((function t(r){while(1){switch(r.prev=r.next){case 0:if(!e.isEdit){r.next=6;break}e.stepCheck=true;r.next=4;return e.getGseDetail({pointId:e.pointId});case 4:r.next=7;break;case 6:e.$nextTick((function(){e.updataLoading(false)}));case 7:case"end":return r.stop()}}}),t)})))()},beforeRouteLeave:function t(e,r,i){this.setToggleDefaultContent();i()},methods:p(p(p(p({},(0,o.mapMutations)(["setToggleDefaultContent"])),(0,o.mapMutations)("config",["updataLoading","updateDetail"])),(0,o.mapActions)("config",["getGseDetail"])),{},{checkedChange:function t(e){this.stepCheck=!!e},stepChange:function t(e){this.curStep=e||this.curStep+1}})};e.default=f},390:function(t,e,r){"use strict";r.r(e);var i=r(391);var a=r.n(i);for(var n in i)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return i[t]}))})(n);e["default"]=a.a},391:function(t,e,r){"use strict";var i=r(1);Object.defineProperty(e,"__esModule",{value:true});e.default=void 0;var a=i(r(5));var n=i(r(6));var s=i(r(17));var o=r(9);var u=i(r(442));var l=i(r(324));var c=i(r(277));var d=i(r(511));var p=r(10);function f(t,e){var r=Object.keys(t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);if(e)i=i.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}));r.push.apply(r,i)}return r}function h(t){for(var e=1;e<arguments.length;e++){var r=arguments[e]!=null?arguments[e]:{};if(e%2){f(Object(r),true).forEach((function(e){(0,s.default)(t,e,r[e])}))}else if(Object.getOwnPropertyDescriptors){Object.defineProperties(t,Object.getOwnPropertyDescriptors(r))}else{f(Object(r)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}}return t}var v={name:"StepHost",components:{VerifyInput:u.default,InputType:l.default,SetupFormTable:d.default},mixins:[c.default],props:{pointId:{type:String,default:""},stepCheck:{type:Boolean,defautl:false},isEdit:{type:Boolean,default:false}},data:function t(){var e=this;var r="^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$";return{checkLoading:false,isInit:true,checkedResult:false,isChecked:false,checkedResultList:[],formData:{name:"",description:"",region_id:"",city_id:"",zk_account:"",zk_password:"",zk_hosts:[{zk_ip:"",zk_port:""}],btfileserver:[{inner_ip:"",outer_ip:""}],dataserver:[{inner_ip:"",outer_ip:""}],taskserver:[{inner_ip:"",outer_ip:""}],package_inner_url:"",package_outer_url:""},labelTableList:[{name:"Zookeeper",key:"zk_hosts",thead:"zkHead"},{name:"Btfileserver",key:"btfileserver",thead:"head"},{name:"Dataserver",key:"dataserver",thead:"head"},{name:"Taskserver",key:"taskserver",thead:"head"}],checkConfig:{zkHead:[{name:this.$t("序号"),width:60},{name:"IP",width:230},{name:"PORT",width:230},{name:"",width:70}],head:[{name:this.$t("序号"),width:60},{name:this.$t("内网IP"),width:230},{name:this.$t("外网IP"),width:230},{name:"",width:70}],zk_hosts:[{prop:"zk_ip",classExt:"ip-input ip-input-inner",required:true,placeholder:window.i18n.t("请输入Zookeeper主机的IP"),rules:[{regx:r,content:this.$t("IP格式不正确")},{content:this.$t("冲突校验",{prop:"IP"}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"zk_ip",type:"zk_hosts"})}}]},{prop:"zk_port",classExt:"ip-input ip-input-outer",placeholder:window.i18n.t("请输入Zookeeper主机的端口号"),rules:[{content:this.$t("数字0_65535"),regx:"^([0-9]|[1-9]\\d{1,3}|[1-5]\\d{4}|6[0-4]\\d{4}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$"},{content:this.$t("冲突校验",{prop:this.$t("端口")}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"zk_port",type:"zk_hosts"})}}]}],btfileserver:[{prop:"inner_ip",classExt:"ip-input ip-input-inner",required:true,placeholder:window.i18n.t("请输入Server的内网IP",{type:"Btfile"}),rules:[{regx:r,content:this.$t("IP格式不正确")},{content:this.$t("冲突校验",{prop:"IP"}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"inner_ip",type:"btfileserver"})}}]},{prop:"outer_ip",classExt:"ip-input ip-input-outer",placeholder:window.i18n.t("请输入Server的外网IP",{type:"Btfile"}),rules:[{regx:r,content:this.$t("IP格式不正确")},{content:this.$t("冲突校验",{prop:"IP"}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"outer_ip",type:"btfileserver"})}}]}],dataserver:[{prop:"inner_ip",classExt:"ip-input ip-input-inner",required:true,placeholder:window.i18n.t("请输入Server的内网IP",{type:"Data"}),rules:[{regx:r,content:this.$t("IP格式不正确")},{content:this.$t("冲突校验",{prop:"IP"}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"inner_ip",type:"dataserver"})}}]},{prop:"outer_ip",classExt:"ip-input ip-input-outer",placeholder:window.i18n.t("请输入Server的外网IP",{type:"Data"}),rules:[{regx:r,content:this.$t("IP格式不正确")},{content:this.$t("冲突校验",{prop:"IP"}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"outer_ip",type:"dataserver"})}}]}],taskserver:[{prop:"inner_ip",classExt:"ip-input ip-input-inner",required:true,placeholder:window.i18n.t("请输入Server的内网IP",{type:"Task"}),rules:[{regx:r,content:this.$t("IP格式不正确")},{content:this.$t("冲突校验",{prop:"IP"}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"inner_ip",type:"taskserver"})}}]},{prop:"outer_ip",classExt:"ip-input ip-input-outer",placeholder:window.i18n.t("请输入Server的外网IP",{type:"Task"}),rules:[{regx:r,content:this.$t("IP格式不正确")},{content:this.$t("冲突校验",{prop:"IP"}),validator:function t(r,i){return e.validateUnique(r,{index:i,prop:"outer_ip",type:"taskserver"})}}]}]},urlReg:/^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w.-]+)+[\w\-._~:/?#[\]@!$&'*+,;=.]+$/,rules:{required:[{required:true,message:this.$t("必填项"),trigger:"blur"}],name:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(e){return/^[A-Za-z0-9_\u4e00-\u9fa5]{3,32}$/.test(e)},message:this.$t("长度为3_32的字符"),trigger:"blur"}],url:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(r){return e.urlReg.test(r)},message:this.$t("URL格式不正确"),trigger:"blur"}]},labelWidth:170}},computed:h(h({},(0,o.mapGetters)("config",["detail"])),{},{relatedContentWidth:function t(){return this.labelWidth+580},firstRelatedInputWidth:function t(){return this.labelWidth+285},zkPasswordType:function t(){if(!(0,p.isEmpty)(this.formData.zk_password)){return"password"}return"text"}}),watch:{formData:{deep:true,handler:function t(){if(this.isInit){this.isInit=false}else{this.checkedResult=false}}}},mounted:function t(){this.initDetail();this.checkedResult=this.stepCheck;this.labelWidth=this.initLabelWidth(this.$refs.formData)},methods:h(h(h({},(0,o.mapMutations)("config",["updateDetail"])),(0,o.mapActions)("config",["requestCheckUsability"])),{},{initDetail:function t(){var e=this;Object.keys(this.formData).forEach((function(t){if(e.detail[t]){e.formData[t]=t==="zk_hosts"||/server/g.test(t)?JSON.parse(JSON.stringify(e.detail[t])):e.detail[t]}}))},checkCommit:function t(){var e=this;this.$refs.formData.validate().then((function(){e.validate((0,n.default)(a.default.mark((function t(){var r,i,n,s,o,u,l;return a.default.wrap((function t(a){while(1){switch(a.prev=a.next){case 0:e.checkLoading=true;r=e.formData,i=r.btfileserver,n=r.dataserver,s=r.taskserver,o=r.package_inner_url,u=r.package_outer_url;a.next=4;return e.requestCheckUsability({btfileserver:i,dataserver:n,taskserver:s,package_inner_url:o,package_outer_url:u});case 4:l=a.sent;e.checkedResult=!!l.test_result;e.checkedResultList=l.test_logs||[];e.isChecked=true;e.checkLoading=false;case 9:case"end":return a.stop()}}}),t)}))))}),(function(){e.validate()}))},submitInfo:function t(){this.updateDetail(this.formData);this.$emit("change",true);this.$emit("step")},addAddress:function t(e,r){if(this.checkLoading)return;this.formData[r].splice(e+1,0,r==="zk_hosts"?{zk_ip:"",zk_port:""}:{inner_ip:"",outer_ip:""})},deleteAddress:function t(e,r){if(this.formData[r].length<=1)return;this.formData[r].splice(e,1)},cancel:function t(){this.$router.push({name:"gseConfig"})},validate:function t(e){var r=this;return new Promise((function(t,i){var a=true;var n=0;var s=r;Object.values(r.$refs.checkItem).forEach((function(r){r.handleValidate((function(r){if(r.show){a=false;i(r);return false}n+=1;if(n===s.$refs.checkItem.length){t(a);if(typeof e==="function"){e(a)}}}))}))}))},getDefaultValidator:function t(){return{show:false,content:"",errTag:true}},validateUnique:function t(e,r){var i=r.prop,a=r.type,n=r.index;var s=false;if(!this.formData[a])return!s;if(["zk_port","zk_ip"].includes(i)){var o=i==="zk_ip"?"zk_port":"zk_ip";var u=this.formData.zk_hosts[n];if((0,p.isEmpty)(u[o])){return!s}s=this.formData[a].some((function(t,e){return e!==n&&t.zk_ip+t.zk_port===u.zk_ip+u.zk_port}))}else{s=this.formData[a].some((function(t,r){return r!==n&&t[i]===e}))}return!s}})};e.default=v},392:function(t,e,r){"use strict";r.r(e);var i=r(393);var a=r.n(i);for(var n in i)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return i[t]}))})(n);e["default"]=a.a},393:function(t,e,r){"use strict";Object.defineProperty(e,"__esModule",{value:true});e.default=void 0;var i={name:"setup-form-table",props:{tableHead:{type:Array,default:function t(){return[]},validator:function t(e){return e&&Array.isArray(e)}}},data:function t(){return{}}};e.default=i},394:function(t,e,r){},395:function(t,e,r){},396:function(t,e,r){"use strict";r.r(e);var i=r(397);var a=r.n(i);for(var n in i)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return i[t]}))})(n);e["default"]=a.a},397:function(t,e,r){"use strict";var i=r(1);Object.defineProperty(e,"__esModule",{value:true});e.default=void 0;var a=i(r(5));var n=i(r(6));var s=i(r(8));var o=i(r(17));var u=i(r(277));var l=r(9);var c=r(10);function d(t,e){var r=Object.keys(t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(t);if(e)i=i.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}));r.push.apply(r,i)}return r}function p(t){for(var e=1;e<arguments.length;e++){var r=arguments[e]!=null?arguments[e]:{};if(e%2){d(Object(r),true).forEach((function(e){(0,o.default)(t,e,r[e])}))}else if(Object.getOwnPropertyDescriptors){Object.defineProperties(t,Object.getOwnPropertyDescriptors(r))}else{d(Object(r)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}}return t}var f={name:"StepInfo",mixins:[u.default],props:{pointId:{type:String,default:""},isEdit:{type:Boolean,default:false}},data:function t(){var e=this;return{submitLoading:false,pathSet:[{type:"linux",title:this.$t("Linux系统的Agent信息"),childrend:[{label:"dataipc",required:true,prop:"linuxDataipc",rules:"linuxDataipc",placeholder:""},{label:this.$t("安装路径"),required:true,prop:"linuxSetupPath",rules:"linuxInstallPath",placeholder:""},{label:this.$t("数据文件路径"),required:true,prop:"linuxDataPath",rules:"linuxPath",placeholder:""},{label:this.$t("运行时路径"),required:true,prop:"linuxRunPath",rules:"linuxPath",placeholder:""},{label:this.$t("日志文件路径"),required:true,prop:"linuxLogPath",rules:"linuxPath",placeholder:""},{label:this.$t("临时文件路径"),required:true,prop:"linuxTempPath",rules:"linuxPath",placeholder:""}]},{type:"windows",title:this.$t("Windows系统的Agent信息"),childrend:[{label:"dataipc",required:true,prop:"windowsDataipc",rules:"winDataipc",placeholder:this.$t("请输入不小于零的整数")},{label:this.$t("安装路径"),required:true,prop:"windowsSetupPath",rules:"winInstallPath",placeholder:""},{label:this.$t("数据文件路径"),required:true,prop:"windowsDataPath",rules:"winPath",placeholder:""},{label:this.$t("日志文件路径"),required:true,prop:"windowsLogPath",rules:"winPath",placeholder:""},{label:this.$t("临时文件路径"),required:true,prop:"windowsTempPath",rules:"winPath",placeholder:""}]}],formData:{linuxDataipc:"/var/run/ipc.state.report.cloud",linuxSetupPath:"/usr/local/gse",linuxDataPath:"/usr/local/gse",linuxRunPath:"/usr/local/gse",linuxLogPath:"/usr/log/gse",linuxTempPath:"/tmp",windowsDataipc:"",windowsSetupPath:"C:\\gse",windowsDataPath:"C:\\gse",windowsLogPath:"C:\\gse\\logs",windowsTempPath:"C:\\tmp"},linuxNotInclude:["/etc/","/root/","/boot/","/dev/","/sys/","/tmp/","/var/","/usr/lib/","/usr/lib64/","/usr/include/","/usr/local/etc/","/usr/local/sa/","/usr/local/lib/","/usr/local/lib64/","/usr/local/bin/","/usr/local/libexec/","/usr/local/sbin/"],linuxNotIncludeError:["/etc","/root","/boot","/dev","/sys","/tmp","/var","/usr/lib","/usr/lib64","/usr/include","/usr/local/etc","/usr/local/sa","/usr/local/lib","/usr/local/lib64","/usr/local/bin","/usr/local/libexec","/usr/local/sbin"],winNotInclude:["C:\\\\Windows\\\\","C:\\\\Windows\\\\","C:\\\\config\\\\","C:\\\\Users\\\\","C:\\\\Recovery\\\\"],winNotIncludeError:["C:\\Windows","C:\\Windows","C:\\config","C:\\Users","C:\\Recovery"],rules:{linuxDataipc:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(e){return/^(\/[A-Za-z0-9_.]{1,}){1,}$/.test(e)},message:this.$t("LinuxIpc校验不正确"),trigger:"blur"}],winDataipc:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(e){return/^(0|[1-9][0-9]*)$/.test(e)},message:this.$t("winIpc校验不正确"),trigger:"blur"}],linuxPath:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(e){return/^(\/[A-Za-z0-9_]{1,16}){1,}$/.test(e)},message:this.$t("Linux路径格式不正确"),trigger:"blur"}],winPath:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(e){return/^([c-zC-Z]:)(\\[A-Za-z0-9_]{1,16}){1,}$/.test(e)},message:this.$t("windows路径格式不正确"),trigger:"blur"}],linuxInstallPath:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(e){return/^(\/[A-Za-z0-9_]{1,16}){2,}$/.test(e)},message:this.$t("Linux路径格式不正确"),trigger:"blur"},{validator:function t(r){var i="".concat(r,"/");return!e.linuxNotInclude.find((function(t){return i.search(t)>-1}))},message:function t(){return e.$t("不能以如下内容开头",{path:e.linuxNotIncludeError.join(", ")})},trigger:"blur"}],winInstallPath:[{required:true,message:this.$t("必填项"),trigger:"blur"},{validator:function t(e){return/^([c-zC-Z]:)(\\[A-Za-z0-9_]{1,16}){1,}$/.test(e)},message:this.$t("windows路径格式不正确"),trigger:"blur"},{validator:function t(r){var i="".concat(r,"\\\\");return!e.winNotInclude.find((function(t){return i.search(new RegExp(t,"i"))>-1}))},message:function t(){return e.$t("不能以如下内容开头",{path:e.winNotIncludeError.join(", ")})},trigger:"blur"}]}}},computed:p({},(0,l.mapGetters)("config",["detail"])),mounted:function t(){this.initConfig();this.initLabelWidth(this.$refs.formData)},methods:p(p({},(0,l.mapActions)("config",["requestCreatePoint","requestEditPoint"])),{},{initConfig:function t(){var e=this;var r=this.detail.agent_config,i=r.linux,a=r.windows;try{var n={};Object.keys(i).forEach((function(t){if(e.isEdit||i[t]){n["linux_".concat(t)]=i[t]||""}}));Object.keys(a).forEach((function(t){if(e.isEdit||a[t]){n["windows_".concat(t)]=a[t]||""}}));(0,s.default)(this.formData,(0,c.transformDataKey)(n))}catch(t){}},submitHandle:function t(){var e=this;this.$refs.formData.validate().then((0,n.default)(a.default.mark((function t(){var r,i,n,o,u,l,d,p,f,h,v,m,b,g,k,_;return a.default.wrap((function t(a){while(1){switch(a.prev=a.next){case 0:r=e.detail,i=r.name,n=r.zk_account,o=r.zk_password,u=r.region_id,l=r.city_id,d=r.zk_hosts,p=r.btfileserver,f=r.dataserver,h=r.taskserver,v=r.package_inner_url,m=r.package_outer_url,b=r.description;e.submitLoading=true;g={linux:{},windows:{}};Object.keys(e.formData).forEach((function(t){if(/linux/gi.test(t)){var r=(0,c.toLine)(t).replace(/linux_/g,"");g.linux[r]=e.formData[t]}if(/windows/gi.test(t)){var i=(0,c.toLine)(t).replace(/windows_/g,"");g.windows[i]=e.formData[t]}}));k={name:i,zk_account:n,region_id:u,city_id:l,zk_hosts:d,btfileserver:p,dataserver:f,taskserver:h,package_inner_url:v,package_outer_url:m,agent_config:g,description:b};if(!e.isEdit||!(0,c.isEmpty)(o)){(0,s.default)(k,{zk_password:o})}if(!e.isEdit){a.next=12;break}a.next=9;return e.requestEditPoint({pointId:e.pointId,data:k});case 9:_=a.sent;a.next=15;break;case 12:a.next=14;return e.requestCreatePoint(k);case 14:_=a.sent;case 15:e.submitLoading=false;if(_){e.$bkMessage({theme:"success",message:e.isEdit?e.$t("修改接入点成功"):e.$t("新增接入点成功")});e.cancel()}case 17:case"end":return a.stop()}}}),t)}))),(function(){}))},stepNext:function t(){this.$emit("step",1)},cancel:function t(){this.$router.push({name:"gseConfig"})},pathRepair:function t(e,r){var i=e[0].trim().replace(/[/\\]+/gi,"/");var a=i.split("/").filter((function(t){return!!t}));if(/linux/gi.test(r)){this.formData[r]="/".concat(a.join("/"))}else{if(r==="windowsDataipc"){return}this.formData[r]=a.join("\\")}}})};e.default=f},398:function(t,e,r){},399:function(t,e,r){},510:function(t,e,r){"use strict";r.r(e);var i=r(575);var a=r(390);for(var n in a)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return a[t]}))})(n);var s=r(513);var o=r(2);var u=Object(o["a"])(a["default"],i["a"],i["b"],false,null,"1cb0eb2a",null);e["default"]=u.exports},511:function(t,e,r){"use strict";r.r(e);var i=r(585);var a=r(392);for(var n in a)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return a[t]}))})(n);var s=r(512);var o=r(2);var u=Object(o["a"])(a["default"],i["a"],i["b"],false,null,"30b6d99f",null);e["default"]=u.exports},512:function(t,e,r){"use strict";var i=r(394);var a=r.n(i);var n=a.a},513:function(t,e,r){"use strict";var i=r(395);var a=r.n(i);var n=a.a},514:function(t,e,r){"use strict";r.r(e);var i=r(577);var a=r(396);for(var n in a)if(["default"].indexOf(n)<0)(function(t){r.d(e,t,(function(){return a[t]}))})(n);var s=r(515);var o=r(2);var u=Object(o["a"])(a["default"],i["a"],i["b"],false,null,"69e90fbe",null);e["default"]=u.exports},515:function(t,e,r){"use strict";var i=r(398);var a=r.n(i);var n=a.a},516:function(t,e,r){"use strict";var i=r(399);var a=r.n(i);var n=a.a},552:function(t,e,r){"use strict";r.d(e,"a",(function(){return i}));r.d(e,"b",(function(){return a}));var i=function(){var t=this;var e=t.$createElement;var r=t._self._c||e;return r("div",{directives:[{name:"bkloading",rawName:"v-bkloading",value:{isLoading:t.loading},expression:"{ isLoading: loading }"}],staticClass:"gse-config-wrapper"},[!t.loading?r("section",{staticClass:"process-wrapper"},[t.curStep===1?r("StepHost",{attrs:{"point-id":t.pointId,"step-check":t.stepCheck,"is-edit":t.isEdit},on:{change:t.checkedChange,step:t.stepChange}}):t._e(),t._v(" "),t.curStep===2?r("StepInfo",{attrs:{"point-id":t.pointId,"is-edit":t.isEdit},on:{step:t.stepChange}}):t._e()],1):t._e()])};var a=[]},575:function(t,e,r){"use strict";r.d(e,"a",(function(){return i}));r.d(e,"b",(function(){return a}));var i=function(){var t=this;var e=t.$createElement;var r=t._self._c||e;return r("div",{staticClass:"access-point-host"},[r("bk-form",{ref:"formData",attrs:{"label-width":t.labelWidth,model:t.formData}},[r("bk-form-item",{attrs:{label:t.$t("接入点名称"),required:true,rules:t.rules.name,property:"name","error-display-type":"normal"}},[r("bk-input",{attrs:{placeholder:t.$t("用户创建的接入点")},model:{value:t.formData.name,callback:function(e){t.$set(t.formData,"name",typeof e==="string"?e.trim():e)},expression:"formData.name"}})],1),t._v(" "),r("bk-form-item",{attrs:{label:t.$t("接入点说明")}},[r("bk-input",{attrs:{"ext-cls":"bg-white textarea-description",type:"textarea",rows:4,maxlength:100,placeholder:t.$t("接入点说明placeholder")},model:{value:t.formData.description,callback:function(e){t.$set(t.formData,"description",typeof e==="string"?e.trim():e)},expression:"formData.description"}})],1),t._v(" "),r("bk-form-item",{attrs:{label:t.$t("区域"),required:true,rules:t.rules.required,property:"region_id","error-display-type":"normal"}},[r("bk-input",{attrs:{placeholder:t.$t("请输入")},model:{value:t.formData.region_id,callback:function(e){t.$set(t.formData,"region_id",typeof e==="string"?e.trim():e)},expression:"formData.region_id"}})],1),t._v(" "),r("bk-form-item",{attrs:{label:t.$t("城市"),required:true,rules:t.rules.required,property:"city_id","error-display-type":"normal"}},[r("bk-input",{attrs:{placeholder:t.$t("请输入")},model:{value:t.formData.city_id,callback:function(e){t.$set(t.formData,"city_id",typeof e==="string"?e.trim():e)},expression:"formData.city_id"}})],1),t._v(" "),r("bk-form-item",{staticClass:"mt40",attrs:{label:t.$t("Zookeeper用户名"),required:true,rules:t.rules.required,property:"zk_account","error-display-type":"normal"}},[r("bk-input",{attrs:{placeholder:t.$t("请输入")},model:{value:t.formData.zk_account,callback:function(e){t.$set(t.formData,"zk_account",typeof e==="string"?e.trim():e)},expression:"formData.zk_account"}})],1),t._v(" "),r("bk-form-item",{attrs:{label:t.$t("Zookeeper密码"),required:!t.isEdit,rules:t.isEdit?[]:t.rules.required,property:"zk_password","error-display-type":"normal"}},[r("bk-input",{attrs:{type:t.zkPasswordType,placeholder:t.$t("请输入")},model:{value:t.formData.zk_password,callback:function(e){t.$set(t.formData,"zk_password",typeof e==="string"?e.trim():e)},expression:"formData.zk_password"}})],1),t._v(" "),t._l(t.labelTableList,(function(e,i){return r("div",{key:i,class:["bk-form-item ip-related-item clearfix",{mb40:!i}],style:{width:t.relatedContentWidth+"px"}},[r("div",{staticClass:"bk-form-item is-required"},[r("label",{staticClass:"bk-label",style:{width:t.labelWidth+"px"}},[r("span",{staticClass:"bk-label-text"},[t._v(t._s(e.name))])]),t._v(" "),r("div",{staticClass:"bk-form-content",style:{"margin-left":t.labelWidth+"px"}},[r("setup-form-table",{ref:"zookeeperTable",refInFor:true,attrs:{"table-head":t.checkConfig[e.thead]}},[r("tbody",{staticClass:"setup-body",attrs:{slot:"tbody"},slot:"tbody"},t._l(t.formData[e.key],(function(i,a){return r("tr",{key:e.key+"td"+a},[r("td",[t._v(t._s(a+1))]),t._v(" "),t._l(t.checkConfig[e.key],(function(n,s){return r("td",{key:e.key+"td"+s,staticClass:"is-required"},[r("verify-input",{ref:"checkItem",refInFor:true,attrs:{position:"right",required:"",rules:n.rules,id:a,"default-validator":t.getDefaultValidator()}},[r("input-type",t._b({model:{value:i[n.prop],callback:function(e){t.$set(i,n.prop,typeof e==="string"?e.trim():e)},expression:"host[config.prop]"}},"input-type",{type:"text",placeholder:t.$t("请输入"),disabled:t.checkLoading},false))],1)],1)})),t._v(" "),r("td",[r("div",{staticClass:"opera-icon-group"},[r("i",{class:["nodeman-icon nc-plus",{"disable-icon":t.checkLoading}],on:{click:function(r){return t.addAddress(a,e.key)}}}),t._v(" "),r("i",{class:["nodeman-icon nc-minus",{"disable-icon":t.formData[e.key].length<=1}],on:{click:function(r){return t.deleteAddress(a,e.key)}}})])])],2)})),0)])],1)])])})),t._v(" "),r("bk-form-item",{staticClass:"mt40",attrs:{label:t.$t("Agent安装包URL"),required:true,rules:t.rules.url,property:"package_inner_url","error-display-type":"normal"}},[r("bk-input",{attrs:{disabled:t.checkLoading,placeholder:t.$t("请输入内网下载URL")},model:{value:t.formData.package_inner_url,callback:function(e){t.$set(t.formData,"package_inner_url",typeof e==="string"?e.trim():e)},expression:"formData.package_inner_url"}})],1),t._v(" "),r("bk-form-item",{staticClass:"mt10",attrs:{label:"",rules:t.rules.url,property:"package_outer_url","error-display-type":"normal"}},[r("bk-input",{attrs:{disabled:t.checkLoading,placeholder:t.$t("请输入外网下载URL")},model:{value:t.formData.package_outer_url,callback:function(e){t.$set(t.formData,"package_outer_url",typeof e==="string"?e.trim():e)},expression:"formData.package_outer_url"}})],1),t._v(" "),r("bk-form-item",{staticClass:"mt30"},[r("bk-button",{staticClass:"check-btn",attrs:{theme:"primary",loading:t.checkLoading,disabled:t.checkedResult},on:{click:function(e){e.stopPropagation();return t.checkCommit(e)}}},[t._v("\n        "+t._s(t.$t("测试Server及URL可用性"))+"\n      ")]),t._v(" "),t.isChecked?r("section",{staticClass:"check-result"},[r("div",{staticClass:"check-result-detail"},[t.isChecked?[r("h4",{staticClass:"result-title"},[t._v(t._s(t.$t("测试结果")))]),t._v(" "),t._l(t.checkedResultList,(function(e,i){return[r("p",{key:i,class:{error:e.log_level==="ERROR"}},[t._v(t._s("- "+e.log))])]}))]:t._e()],2)]):t._e()],1),t._v(" "),r("bk-form-item",{staticClass:"item-button-group mt30"},[r("bk-button",{staticClass:"nodeman-primary-btn",attrs:{theme:"primary",disabled:!t.checkedResult||t.checkLoading},on:{click:t.submitInfo}},[t._v("\n        "+t._s(t.$t("下一步"))+"\n      ")]),t._v(" "),r("bk-button",{staticClass:"nodeman-cancel-btn",on:{click:t.cancel}},[t._v("\n        "+t._s(t.$t("取消"))+"\n      ")])],1)],2)],1)};var a=[]},577:function(t,e,r){"use strict";r.d(e,"a",(function(){return i}));r.d(e,"b",(function(){return a}));var i=function(){var t=this;var e=t.$createElement;var r=t._self._c||e;return r("div",{staticClass:"access-point-info"},[r("bk-form",{ref:"formData",attrs:{"label-width":120,model:t.formData}},[t._l(t.pathSet,(function(e,i){return[r("h3",{key:i,class:["block-title",{mt40:!i}]},[t._v(t._s(e.title))]),t._v(" "),t._l(e.childrend,(function(i,a){return r("bk-form-item",{key:e.type+"-"+a,attrs:{"error-display-type":"normal",label:i.label,property:i.prop,required:i.required,rules:t.rules[i.rules]}},[r("bk-input",{attrs:{placeholder:i.placeholder||t.$t("请输入")},on:{blur:function(e){return t.pathRepair(arguments,i.prop)}},model:{value:t.formData[i.prop],callback:function(e){t.$set(t.formData,i.prop,typeof e==="string"?e.trim():e)},expression:"formData[path.prop]"}})],1)}))]})),t._v(" "),r("bk-form-item",{staticClass:"mt30 item-button-group"},[r("bk-button",{staticClass:"nodeman-primary-btn",attrs:{theme:"primary",disabled:t.submitLoading},on:{click:function(e){e.stopPropagation();e.preventDefault();return t.submitHandle(e)}}},[t._v("\n        "+t._s(t.$t("确认"))+"\n      ")]),t._v(" "),r("bk-button",{staticClass:"nodeman-cancel-btn",attrs:{disabled:t.submitLoading},on:{click:t.stepNext}},[t._v("\n        "+t._s(t.$t("上一步"))+"\n      ")]),t._v(" "),r("bk-button",{staticClass:"nodeman-cancel-btn",attrs:{disabled:t.submitLoading},on:{click:t.cancel}},[t._v("\n        "+t._s(t.$t("取消"))+"\n      ")])],1)],2)],1)};var a=[]},585:function(t,e,r){"use strict";r.d(e,"a",(function(){return i}));r.d(e,"b",(function(){return a}));var i=function(){var t=this;var e=t.$createElement;var r=t._self._c||e;return r("div",{staticClass:"setup"},[r("div",{staticClass:"setup-header-wrapper"},[r("table",[r("colgroup",t._l(t.tableHead,(function(t,e){return r("col",{key:e,attrs:{width:t.width?t.width:"auto"}})})),0),t._v(" "),r("thead",{staticClass:"setup-header"},[r("tr",t._l(t.tableHead,(function(e,i){return r("th",{key:i},[t._v("\n            "+t._s(e.name)+"\n          ")])})),0)])])]),t._v(" "),r("div",{staticClass:"setup-body-wrapper"},[r("div",{staticClass:"body-content"},[r("table",[r("colgroup",t._l(t.tableHead,(function(t,e){return r("col",{key:e,attrs:{width:t.width?t.width:"auto"}})})),0),t._v(" "),t._t("tbody")],2)])])])};var a=[]}}]);