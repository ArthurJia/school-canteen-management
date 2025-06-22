<template>
  <div :id="containerId" :style="{ width: '100%', height: height }"></div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import 'luckysheet/dist/plugins/css/pluginsCss.css';
import 'luckysheet/dist/plugins/plugins.css';
import 'luckysheet/dist/css/luckysheet.css';
import 'luckysheet/dist/assets/iconfont/iconfont.css';

export default {
  name: 'LuckysheetWrapper',
  props: {
    options: {
      type: Object,
      default: () => ({})
    },
    height: {
      type: String,
      default: '600px'
    },
    containerId: {
      type: String,
      default: 'luckysheet'
    }
  },
  emits: ['initialized', 'updated'],
  setup(props, { emit }) {
    const luckysheetInstance = ref(null);

    // 加载jQuery
    const loadJQuery = async () => {
      if (typeof window.$ !== 'undefined' && typeof window.jQuery !== 'undefined') {
        console.log('jQuery已存在');
        return;
      }

      console.log('开始加载jQuery...');
      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js';
        script.onload = () => {
          console.log('jQuery加载完成');
          resolve();
        };
        script.onerror = () => {
          reject(new Error('加载jQuery失败'));
        };
        document.head.appendChild(script);
      });
    };

    // 确保jQuery已加载
    const ensureJQuery = async () => {
      try {
        await loadJQuery();
      } catch (error) {
        console.error('确保jQuery加载时出错:', error);
        throw error;
      }
    };

    // 动态导入luckysheet
    const importLuckysheet = async () => {
      try {
        await ensureJQuery();
        const luckysheetModule = await import('luckysheet');
        return luckysheetModule.default;
      } catch (error) {
        console.error('加载luckysheet模块失败:', error);
        throw error;
      }
    };

    // 初始化luckysheet
    const initLuckysheet = async () => {
      try {
        const luckysheet = await importLuckysheet();
        
        // 合并默认选项和传入的选项
        const defaultOptions = {
          container: props.containerId,
          lang: 'zh',
          showinfobar: false,
          allowUpdate: true,
          showtoolbar: true,
          showsheetbar: true,
          showstatisticBar: true,
          enableAddRow: true,
          enableAddCol: true,
          showRowBar: true,
          showColumnBar: true,
          sheetFormulaBar: true,
          hook: {
            updated: () => {
              const currentData = luckysheet.getAllSheets();
              emit('updated', currentData);
            }
          }
        };

        const options = { ...defaultOptions, ...props.options };
        
        luckysheetInstance.value = luckysheet.create(options);
        emit('initialized', luckysheetInstance.value);
        
        return luckysheetInstance.value;
      } catch (error) {
        console.error('初始化luckysheet失败:', error);
        throw error;
      }
    };

    // 获取当前表格数据
    const getAllSheets = () => {
      if (!window.luckysheet) return null;
      return window.luckysheet.getAllSheets();
    };

    // 导出Excel
    const exportExcel = (fileName) => {
      if (!window.luckysheet) return;
      window.luckysheet.exportExcel(fileName);
    };

    onMounted(async () => {
      try {
        await initLuckysheet();
      } catch (error) {
        console.error('组件挂载时初始化luckysheet失败:', error);
      }
    });

    onBeforeUnmount(() => {
      if (window.luckysheet) {
        try {
          window.luckysheet.destroy();
        } catch (error) {
          console.error('销毁luckysheet实例失败:', error);
        }
      }
    });

    // 暴露方法给父组件
    return {
      getAllSheets,
      exportExcel
    };
  }
};
</script>