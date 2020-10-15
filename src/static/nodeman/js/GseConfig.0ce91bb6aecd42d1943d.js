(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[12],{260:function(t,e,s){"use strict";s.r(e);var a=s(553);var n=s(379);for(var i in n)if(["default"].indexOf(i)<0)(function(t){s.d(e,t,(function(){return n[t]}))})(i);var r=s(509);var o=s(2);var c=Object(o["a"])(n["default"],a["a"],a["b"],false,null,"167a2979",null);e["default"]=c.exports},379:function(t,e,s){"use strict";s.r(e);var a=s(380);var n=s.n(a);for(var i in a)if(["default"].indexOf(i)<0)(function(t){s.d(e,t,(function(){return a[t]}))})(i);e["default"]=n.a},380:function(t,e,s){"use strict";var a=s(1);Object.defineProperty(e,"__esModule",{value:true});e.default=void 0;var n=a(s(5));var i=a(s(275));var r=a(s(6));var o=a(s(17));var c=s(9);var u=s(13);var l=a(s(441));var d=a(s(502));var p=a(s(272));var v=a(s(447));function f(t,e){var s=Object.keys(t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);if(e)a=a.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}));s.push.apply(s,a)}return s}function _(t){for(var e=1;e<arguments.length;e++){var s=arguments[e]!=null?arguments[e]:{};if(e%2){f(Object(s),true).forEach((function(e){(0,o.default)(t,e,s[e])}))}else if(Object.getOwnPropertyDescriptors){Object.defineProperties(t,Object.getOwnPropertyDescriptors(s))}else{f(Object(s)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(s,e))}))}}return t}var h={name:"GseConfig",components:{RightPanel:l.default,AccessPointTable:d.default,Tips:p.default,ExceptionCard:v.default},data:function t(){return{loading:true,tipsList:[this.$t("gseTopTips1"),this.$t("gseTopTips2")],accessPointList:[],apCreatePermission:false}},computed:_({},(0,c.mapGetters)(["permissionSwitch"])),mounted:function t(){if(this.permissionSwitch){this.getCreatePermission()}this.getAccessPointList()},methods:_(_({},(0,c.mapActions)("config",["requestAccessPointList","requestAccessPointIsUsing","requestDeletetPoint","requestPluginBase","getApPermission"])),{},{getAccessPointList:function t(){var e=this;return(0,r.default)(n.default.mark((function t(){var s;var a,r,o;return n.default.wrap((function t(n){while(1){switch(n.prev=n.next){case 0:e.loading=true;n.next=3;return e.requestAccessPointList();case 3:a=n.sent;a.forEach((function(t){t.is_used=true}));(s=e.accessPointList).splice.apply(s,[0,e.accessPointList.length].concat((0,i.default)(a)));e.loading=false;n.next=9;return e.requestAccessPointIsUsing();case 9:r=n.sent;if(r){a.forEach((function(t){t.is_used=t.is_default||r.some((function(e){return e===t.id}))}));(o=e.accessPointList).splice.apply(o,[0,e.accessPointList.length].concat((0,i.default)(a)))}case 11:case"end":return n.stop()}}}),t)})))()},operaHandler:function t(e,s){var a=this;if(s==="delete"){this.$bkInfo({type:"warning",title:this.$t("确认删除此接入点"),confirmFn:function(){var t=(0,r.default)(n.default.mark((function t(s){var i,r;return n.default.wrap((function t(n){while(1){switch(n.prev=n.next){case 0:s.close();a.loading=true;n.next=4;return a.requestDeletetPoint({pointId:e.id});case 4:i=n.sent;if(!!i&&i.result){r=a.accessPointList.findIndex((function(t){return t.id===e.id}));a.accessPointList.splice(r,1);a.$bkMessage({theme:"success",message:a.$t("删除接入点成功")})}a.loading=false;case 7:case"end":return n.stop()}}}),t)})));function s(e){return t.apply(this,arguments)}return s}()})}else{var i={name:"accessPoint"};if(s!=="add"){i.params={pointId:"".concat(e.id)}}this.$router.push(i)}},getCreatePermission:function t(){var e=this;return(0,r.default)(n.default.mark((function t(){var s;return n.default.wrap((function t(a){while(1){switch(a.prev=a.next){case 0:a.next=2;return e.getApPermission();case 2:s=a.sent;e.apCreatePermission=s.create_action;case 4:case"end":return a.stop()}}}),t)})))()},handleApplyPermission:function t(e){u.bus.$emit("show-permission-modal",{apply_info:[{action:"ap_view",instance_id:e.id,instance_name:e.name}]})}})};e.default=h},381:function(t,e,s){"use strict";s.r(e);var a=s(382);var n=s.n(a);for(var i in a)if(["default"].indexOf(i)<0)(function(t){s.d(e,t,(function(){return a[t]}))})(i);e["default"]=n.a},382:function(t,e,s){"use strict";var a=s(1);Object.defineProperty(e,"__esModule",{value:true});e.default=void 0;var n=a(s(8));var i={name:"AccessPointTable",props:{accessPoint:{type:Object,default:function t(){return{}}}},data:function t(){return{pathMap:{dataipc:"dataipc",setup_path:this.$t("安装路径"),data_path:this.$t("数据文件路径"),run_path:this.$t("运行时路径"),log_path:this.$t("日志文件路径"),temp_path:this.$t("临时文件路径")},serversMap:["BtfileServer","DataServer","TaskServer"],sortLinux:["dataipc","setup_path","data_path","run_path","log_path"],sortWin:["dataipc","setup_path","data_path","log_path"],formData:{}}},computed:{rowspanNum:function t(){var e=this;var s={servers:0,agent:0,linux:this.sortLinux.length,windows:this.sortWin.length};this.serversMap.forEach((function(t){s.servers+=e.accessPoint[t]?e.accessPoint[t].length:0}));s.agent=s.linux+s.windows+1;return s},zookeeper:function t(){if(this.accessPoint.zk_hosts){return this.accessPoint.zk_hosts.map((function(t){return"".concat(t.zk_ip,":").concat(t.zk_port)})).join(",")}return""}},created:function t(){this.resetData()},methods:{resetData:function t(){var e=this;var s=this.accessPoint.agent_config,a=s.linux,i=s.windows;var r=this.sortLinux.map((function(t){return{name:e.pathMap[t],value:a[t]}}));var o=this.sortWin.map((function(t){return{name:e.pathMap[t],value:i[t]}}));this.formData=(0,n.default)({},this.accessPoint,{linux:r,windows:o})}}};e.default=i},383:function(t,e,s){},387:function(t,e,s){},502:function(t,e,s){"use strict";s.r(e);var a=s(571);var n=s(381);for(var i in n)if(["default"].indexOf(i)<0)(function(t){s.d(e,t,(function(){return n[t]}))})(i);var r=s(503);var o=s(2);var c=Object(o["a"])(n["default"],a["a"],a["b"],false,null,null,null);e["default"]=c.exports},503:function(t,e,s){"use strict";var a=s(383);var n=s.n(a);var i=n.a},509:function(t,e,s){"use strict";var a=s(387);var n=s.n(a);var i=n.a},553:function(t,e,s){"use strict";s.d(e,"a",(function(){return a}));s.d(e,"b",(function(){return n}));var a=function(){var t=this;var e=t.$createElement;var s=t._self._c||e;return s("div",{directives:[{name:"bkloading",rawName:"v-bkloading",value:{isLoading:t.loading},expression:"{ isLoading: loading }"}],staticClass:"gse-config-wrapper"},[[s("Tips",{staticClass:"mb20",attrs:{list:t.tipsList}}),t._v(" "),s("auth-component",{staticClass:"mb14",attrs:{tag:"div",auth:{permission:t.apCreatePermission,apply_info:[{action:"ap_create"}]}},scopedSlots:t._u([{key:"default",fn:function(e){var a=e.disabled;return[s("bk-button",{staticClass:"w100",attrs:{theme:"primary",disabled:a},on:{click:function(e){e.stopPropagation();return t.operaHandler(e,"add")}}},[t._v("\n          "+t._s(t.$t("新建"))+"\n        ")])]}}])}),t._v(" "),s("section",{staticClass:"access-point-collapse"},[t._l(t.accessPointList,(function(e){return[s("RightPanel",{key:e.id,staticClass:"access-point-item",attrs:{"align-center":false,"need-border":true,"collapse-color":"#313238","title-bg-color":"#FAFBFD",collapse:e.collapse},on:{"update:collapse":function(s){return t.$set(e,"collapse",s)}}},[s("div",{staticClass:"collapse-header",attrs:{slot:"title"},slot:"title"},[s("div",{staticClass:"access-point-status"},[e.status?s("div",{staticClass:"col-status"},[s("span",{class:"status-mark status-"+e.status.toLocaleLowerCase()})]):s("div",{staticClass:"col-status"},[s("span",{staticClass:"status-mark status-unknown"})])]),t._v(" "),s("div",{staticClass:"header-title"},[s("div",{staticClass:"block-flex"},[s("h3",{staticClass:"access-point-title"},[t._v("\n                  "+t._s(e.name)+"\n                ")]),t._v(" "),e.ap_type==="system"?s("span",{staticClass:"title-tag"},[t._v(t._s(t.$t("默认")))]):t._e(),t._v(" "),s("auth-component",{attrs:{tag:"div",auth:{permission:e.edit,apply_info:[{action:"ap_edit",instance_id:e.id,instance_name:e.name}]}},scopedSlots:t._u([{key:"default",fn:function(a){var n=a.disabled;return[s("bk-button",{attrs:{"ext-cls":"access-point-operation",text:"",disabled:n},on:{click:function(s){s.stopPropagation();return t.operaHandler(e,"edit")}}},[s("i",{staticClass:"nodeman-icon nc-icon-edit-2"})])]}}],null,true)}),t._v(" "),s("auth-component",{attrs:{tag:"div",auth:{permission:e.delete,apply_info:[{action:"ap_delete",instance_id:e.id,instance_name:e.name}]}},scopedSlots:t._u([{key:"default",fn:function(a){var n=a.disabled;return[s("bk-popover",{attrs:{placement:"top",disabled:!e.is_used}},[e.ap_type!=="system"?s("bk-button",{attrs:{"ext-cls":"access-point-operation",text:"",disabled:n||e.is_used},on:{click:function(s){s.stopPropagation();return t.operaHandler(e,"delete")}}},[s("i",{staticClass:"nodeman-icon nc-delete-2"})]):t._e(),t._v(" "),s("div",{attrs:{slot:"content"},slot:"content"},[t._v(t._s(t.$t("该接入点被使用中无法删除")))])],1)]}}],null,true)})],1),t._v(" "),e.description?s("p",{staticClass:"access-point-remarks"},[s("span",[t._v("ID:")]),t._v(" "),s("span",{staticClass:"point-id"},[t._v(t._s("  "+(e.id||"--")))]),t._v(" "),e.description?s("span",{staticClass:"point-desc"},[t._v(t._s(e.description))]):t._e()]):t._e()])]),t._v(" "),s("div",{staticClass:"collapse-container",attrs:{slot:""},slot:"default"},[e.view?s("AccessPointTable",{staticClass:"not-outer-border",attrs:{"access-point":e}}):s("exception-card",{attrs:{type:"notPower","has-border":false},on:{click:function(s){return t.handleApplyPermission(e)}}})],1)])]}))],2)]],2)};var n=[]},571:function(t,e,s){"use strict";s.d(e,"a",(function(){return a}));s.d(e,"b",(function(){return n}));var a=function(){var t=this;var e=t.$createElement;var s=t._self._c||e;return s("div",[s("table",{staticClass:"access-point-table"},[t._m(0),t._v(" "),s("tbody",[s("tr",[s("td",{attrs:{rowspan:t.rowspanNum.servers+3}},[t._v(t._s(t.$t("Server信息")))]),t._v(" "),s("td",{attrs:{rowspan:"2"}},[t._v(t._s(t.$t("地域信息")))]),t._v(" "),s("td",[t._v(t._s(t.$t("区域")))]),t._v(" "),s("td",{staticClass:"table-content"},[t._v(t._s(t.formData.region_id))])]),t._v(" "),s("tr",[s("td",[t._v(t._s(t.$t("城市")))]),t._v(" "),s("td",{staticClass:"table-content"},[t._v(t._s(t.formData.city_id))])]),t._v(" "),s("tr",[s("td",[t._v("Zookeeper")]),t._v(" "),s("td",[t._v(t._s(t.$t("集群地址")))]),t._v(" "),s("td",{staticClass:"table-content"},[t._v(t._s(t.zookeeper))])]),t._v(" "),t._l(t.serversMap,(function(e,a){return t._l(t.formData[e],(function(n,i){return s("tr",{key:"server"+(a+i)},[s("td",[t._v(t._s(e+" "+(i+1)))]),t._v(" "),s("td",[t._v("IP")]),t._v(" "),s("td",{staticClass:"table-content"},[t._v(t._s(t.$t("内网")+n.inner_ip+";  "+(t.$t("外网")+n.outer_ip)))])])}))})),t._v(" "),s("tr",[s("td",{attrs:{rowspan:t.rowspanNum.agent}},[t._v(t._s(t.$t("Agent信息")))]),t._v(" "),s("td",[t._v(t._s(t.$t("安装包")))]),t._v(" "),s("td",[t._v("URL")]),t._v(" "),s("td",{staticClass:"table-content"},[t._v(t._s(t.$t("内网")+t.formData.package_inner_url+";  "+(t.$t("外网")+t.formData.package_outer_url)))])]),t._v(" "),t.rowspanNum.linux?t._l(t.formData.linux,(function(e,a){return s("tr",{key:a+100},[a===0?s("td",{attrs:{rowspan:t.rowspanNum.linux}},[t._v("Linux")]):t._e(),t._v(" "),s("td",[t._v(t._s(e.name))]),t._v(" "),s("td",{staticClass:"table-content"},[t._v(t._s(e.value))])])})):t._e(),t._v(" "),t.rowspanNum.windows?t._l(t.formData.windows,(function(e,a){return s("tr",{key:a+200},[a===0?s("td",{attrs:{rowspan:t.rowspanNum.windows}},[t._v("Windows")]):t._e(),t._v(" "),s("td",[t._v(t._s(e.name))]),t._v(" "),s("td",{staticClass:"table-content"},[t._v(t._s(e.value))])])})):t._e()],2)])])};var n=[function(){var t=this;var e=t.$createElement;var s=t._self._c||e;return s("thead",[s("tr",[s("th",{attrs:{with:"125"}}),t._v(" "),s("th",{attrs:{with:"100"}}),t._v(" "),s("th",{attrs:{with:"100"}}),t._v(" "),s("th",{attrs:{with:"735"}})])])}]}}]);