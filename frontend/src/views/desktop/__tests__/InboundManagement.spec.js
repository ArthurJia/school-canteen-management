import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import InboundManagement from '../InboundManagement.vue'
import { ElCard, ElForm, ElFormItem, ElInput, ElSelect, ElButton, ElAlert } from 'element-plus'

// Mock Element Plus components
const mockComponents = {
  ElCard,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElButton,
  ElAlert
}

describe('InboundManagement.vue', () => {
  // 测试组件渲染
  it('renders properly', () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    expect(wrapper.find('.inbound-management').exists()).toBe(true)
    expect(wrapper.find('.card-header').text()).toBe('食材入库')
  })

  // 测试表单字段初始值
  it('initializes with correct default values', () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    const { form } = wrapper.vm
    expect(form.name).toBe('')
    expect(form.category).toBe('')
    expect(form.supplier).toBe('')
    expect(form.quantity).toBe(1)
    expect(form.price).toBe(0)
    expect(form.remark).toBe('')
  })

  // 测试小计计算
  it('calculates subtotal correctly', async () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    await wrapper.setData({
      form: {
        quantity: 2,
        price: 10
      }
    })
    
    expect(wrapper.vm.subtotal).toBe('20.00')
  })

  // 测试分类选项
  it('has correct category options', () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    const categories = wrapper.vm.categories
    expect(categories).toContainEqual({ value: 'vegetable', label: '蔬菜类' })
    expect(categories).toContainEqual({ value: 'meat', label: '鲜肉类' })
    expect(categories.length).toBeGreaterThan(0)
  })

  // 测试供应商选项
  it('has correct supplier options', () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    const suppliers = wrapper.vm.suppliers
    expect(suppliers).toContainEqual({ value: 'maidelong', label: '麦德龙' })
    expect(suppliers.length).toBeGreaterThan(0)
  })

  // 测试表单提交
  it('handles form submission', async () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    const consoleSpy = vi.spyOn(console, 'log')
    
    // 填写表单
    await wrapper.setData({
      form: {
        name: '测试食材',
        category: 'vegetable',
        supplier: 'maidelong',
        quantity: 2,
        price: 10,
        remark: '测试备注'
      }
    })
    
    // 触发提交
    await wrapper.find('button').trigger('click')
    
    // 验证console.log被调用
    expect(consoleSpy).toHaveBeenCalledWith('提交表单:', {
      name: '测试食材',
      category: 'vegetable',
      supplier: 'maidelong',
      quantity: 2,
      price: 10,
      remark: '测试备注'
    })
  })

  // 测试数量输入限制
  it('validates quantity input', async () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    const quantityInput = wrapper.find('input[type="number"]')
    expect(quantityInput.attributes('min')).toBe('1')
  })

  // 测试价格输入限制
  it('validates price input', async () => {
    const wrapper = mount(InboundManagement, {
      global: {
        components: mockComponents
      }
    })
    
    const priceInput = wrapper.find('input[type="number"]').next()
    expect(priceInput.attributes('min')).toBe('0')
    expect(priceInput.attributes('step')).toBe('0.01')
  })
})