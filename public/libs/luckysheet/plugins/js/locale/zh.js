(function () {
    window.luckysheetDemoData = {
        functionlist: [
            {
                "n": "SUMIF",
                "t": "数学",
                "d": "对范围中符合指定条件的值求和。",
                "a": "对范围中符合指定条件的值求和。",
                "p": [
                    {
                        "name": "range",
                        "detail": "要根据条件进行检测的范围。"
                    },
                    {
                        "name": "criteria",
                        "detail": "要应用于范围的模式或测试条件。"
                    },
                    {
                        "name": "sum_range",
                        "detail": "[可选] - 要求和的实际单元格。如果省略，则使用range进行求和。"
                    }
                ]
            },
            {
                "n": "SUM",
                "t": "数学",
                "d": "返回一组数值的和。",
                "a": "返回一组数值的和。",
                "p": [
                    {
                        "name": "number1",
                        "detail": "要相加的第一个数值或范围。"
                    },
                    {
                        "name": "number2, ...",
                        "detail": "[可选] - 要相加的其他数值或范围，最多可包含255个。"
                    }
                ]
            },
            {
                "n": "AVERAGE",
                "t": "统计",
                "d": "返回其参数的平均值。",
                "a": "返回其参数的平均值。",
                "p": [
                    {
                        "name": "number1",
                        "detail": "计算平均值时要使用的第一个数值或范围。"
                    },
                    {
                        "name": "number2, ...",
                        "detail": "[可选] - 计算平均值时要使用的其他数值或范围，最多可包含255个。"
                    }
                ]
            }
        ]
    }

    window.luckysheet_locale_zh = {
        functionButton: {
            "button": "按钮",
        },
        currencyDetail: {
            "RMB": "人民币",
            "USdollar": "美元",
            "EUR": "欧元",
            "GBP": "英镑",
            "HK": "港币",
            "JPY": "日元"
        },
        defaultFmt: [
            {
                "text": "自动",
                "value": "General",
                "example": ""
            },
            {
                "text": "纯文本",
                "value": "@",
                "example": ""
            },
            {
                "text": "数值",
                "value": "##0.00",
                "example": "1000.12"
            },
            {
                "text": "百分比",
                "value": "#0.00%",
                "example": "10.12%"
            },
            {
                "text": "科学计数",
                "value": "0.00E+00",
                "example": "1.01E+03"
            }
        ],
        button: {
            "confirm": "确认",
            "cancel": "取消",
            "close": "关闭",
            "update": "更新",
            "delete": "删除",
            "insert": "插入"
        },
        menu: {
            "file": "文件",
            "edit": "编辑",
            "data": "数据",
            "view": "视图",
            "format": "格式",
            "tools": "工具",
            "chart": "图表",
            "help": "帮助"
        },
        toolbar: {
            "undo": "撤销",
            "redo": "重做",
            "paintFormat": "格式刷",
            "currencyFormat": "货币格式",
            "percentageFormat": "百分比格式",
            "numberDecrease": "减少小数位数",
            "numberIncrease": "增加小数位数",
            "moreFormats": "更多格式",
            "font": "字体",
            "fontSize": "字号",
            "bold": "粗体",
            "italic": "斜体",
            "strikethrough": "删除线",
            "underline": "下划线",
            "textColor": "文字颜色",
            "fillColor": "填充颜色",
            "border": "边框",
            "mergeCell": "合并单元格",
            "horizontalAlign": "水平对齐",
            "verticalAlign": "垂直对齐",
            "textWrap": "文本换行",
            "textRotate": "文本旋转",
            "insertImage": "插入图片",
            "insertLink": "插入链接",
            "insertFormula": "插入公式",
            "insertChart": "插入图表",
            "insertComment": "插入批注",
            "conditionalFormat": "条件格式",
            "freezeCell": "冻结单元格",
            "sortAndFilter": "排序和筛选",
            "moreOptions": "更多选项"
        },
        rightclick: {
            "copy": "复制",
            "paste": "粘贴",
            "cut": "剪切",
            "insert": "插入",
            "delete": "删除",
            "hide": "隐藏",
            "unhide": "取消隐藏",
            "row": "行",
            "column": "列",
            "sheet": "工作表",
            "clearContent": "清除内容",
            "sort": "排序",
            "filter": "筛选",
            "chart": "图表",
            "image": "图片",
            "link": "链接",
            "data": "数据",
            "cellFormat": "设置单元格格式"
        },
        formula: {
            "sum": "求和",
            "average": "平均值",
            "count": "计数",
            "max": "最大值",
            "min": "最小值",
            "if": "如果",
            "and": "与",
            "or": "或",
            "concat": "拼接",
            "now": "现在",
            "today": "今天",
            "vlookup": "垂直查找",
            "hlookup": "水平查找",
            "index": "索引",
            "match": "匹配",
            "text": "文本",
            "date": "日期",
            "time": "时间",
            "logical": "逻辑",
            "lookup": "查找",
            "math": "数学",
            "statistical": "统计"
        },
        sheetconfig: {
            "delete": "删除",
            "copy": "复制",
            "rename": "重命名",
            "hide": "隐藏",
            "unhide": "取消隐藏",
            "moveLeft": "向左移",
            "moveRight": "向右移",
            "color": "颜色",
            "addSheet": "添加工作表"
        },
        dataverfication: {
            "title": "数据验证",
            "allowlist": "允许",
            "number": "数字",
            "date": "日期",
            "dropdown": "下拉列表",
            "textlength": "文本长度",
            "custom": "自定义",
            "between": "介于",
            "notbetween": "不介于",
            "equalto": "等于",
            "notequalto": "不等于",
            "greaterthan": "大于",
            "lessthan": "小于",
            "greaterthanorequalto": "大于等于",
            "lessthanorequalto": "小于等于",
            "includenull": "包含空值",
            "source": "来源",
            "tips": "提示",
            "allowedit": "允许编辑"
        },
        comment: {
            "title": "批注",
            "delete": "删除",
            "edit": "编辑",
            "hide": "隐藏",
            "show": "显示",
            "addComment": "添加批注"
        },
        screenshot: {
            "screenshotTipNoSelection": "请选择需要截图的区域",
            "screenshotTipTitle": "提示：",
            "screenshotTipHasCellComponent": "截图中包含批注、下拉列表、按钮等元素，这些内容将不被截取。",
            "screenshotTipHasCell": "截图中包含合并单元格，建议截取完整的合并单元格。",
            "screenshotTipSuccess": "截取成功",
            "screenshotImageName": "截图",
            "downLoadClose": "关闭",
            "downLoadCopy": "复制到剪切板",
            "downLoadBtn": "下载",
            "browserNotTip": "下载功能IE浏览器不支持！",
            "rightclickTip": "请在图片上右键点击另存为",
            "successTip": "已成功复制到剪切板！"
        },
        splitText: {
            "splitDelimiters": "分隔符号",
            "splitOther": "其他",
            "splitContinueSymbol": "连续分隔符号视为一个",
            "splitDataPreview": "数据预览",
            "splitTextTitle": "文本分列",
            "splitConfirmToExe": "这里已有数据，是否替换？",
            "tipNoMulti": "不能对多重选择区域执行此操作",
            "tipNoMultiColumn": "一次只能转换一列数据，选定区域可以包含多列，但会按列进行转换"
        },
        imageText: {
            "imageSetting": "图片设置",
            "close": "关闭",
            "conventional": "常规",
            "moveCell1": "移动并调整单元格大小",
            "moveCell2": "移动并且不调整单元格的大小",
            "moveCell3": "不要移动单元格并调整其大小",
            "fixedPos": "固定位置",
            "border": "边框",
            "width": "宽度",
            "radius": "半径",
            "style": "样式",
            "solid": "实线",
            "dashed": "虚线",
            "dotted": "点状",
            "double": "双线",
            "color": "颜色"
        },
        punctuation: {
            "tab": "Tab 键",
            "semicolon": "分号",
            "comma": "逗号",
            "space": "空格"
        },
        findAndReplace: {
            "find": "查找",
            "replace": "替换",
            "findAll": "查找全部",
            "replaceAll": "替换全部",
            "regexNotTip": "当前浏览器不支持正则表达式！",
            "findReplaceEmpty": "查找替换内容不能为空！",
            "noFindTip": "没有查找到该内容！",
            "modeTip": "该功能不支持多重选择区域！",
            "searchDirection": "搜索方向",
            "searchUp": "向上",
            "searchDown": "向下",
            "searchByRow": "按行",
            "searchByColumn": "按列",
            "searchValue": "查找内容",
            "replaceValue": "替换内容",
            "searchType": "匹配类型",
            "searchCaseSensitive": "区分大小写",
            "searchRegex": "正则表达式匹配",
            "searchFullCell": "整个单元格匹配",
            "searchAllSheets": "搜索所有工作表",
            "searchInFormulas": "在公式中搜索",
            "searchInValues": "在值中搜索",
            "searchInComments": "在批注中搜索"
        }
    }
})();