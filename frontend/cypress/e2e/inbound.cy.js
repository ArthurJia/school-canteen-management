describe('食材入库功能', () => {
  beforeEach(() => {
    // 访问入库管理页面
    cy.visit('/inbound')
    
    // 等待页面加载完成
    cy.contains('食材入库').should('be.visible')
  })

  it('应该显示入库表单', () => {
    // 验证表单元素存在
    cy.get('.inbound-form').should('exist')
    cy.get('input[placeholder="请输入食材名称"]').should('exist')
    cy.get('.el-select').should('exist')
    cy.get('input[type="number"]').should('exist')
    cy.get('button').contains('提交').should('exist')
  })

  it('应该能够选择食材分类', () => {
    // 点击分类下拉框
    cy.get('.el-select').eq(0).click()
    
    // 选择"蔬菜类"
    cy.contains('蔬菜类').click()
    
    // 验证选择结果
    cy.get('.el-select').eq(0).should('contain', '蔬菜类')
  })

  it('应该能够选择供应商', () => {
    // 点击供应商下拉框
    cy.get('.el-select').eq(1).click()
    
    // 选择"麦德龙"
    cy.contains('麦德龙').click()
    
    // 验证选择结果
    cy.get('.el-select').eq(1).should('contain', '麦德龙')
  })

  it('应该能够输入数量和价格', () => {
    // 输入数量
    cy.get('input[type="number"]').eq(0).clear().type('5')
    
    // 输入价格
    cy.get('input[type="number"]').eq(1).clear().type('10.5')
    
    // 验证小计计算
    cy.contains('小计: ¥52.50').should('exist')
  })

  it('应该能够提交表单', () => {
    // 填写表单
    cy.get('input[placeholder="请输入食材名称"]').type('测试食材')
    
    // 选择分类
    cy.get('.el-select').eq(0).click()
    cy.contains('蔬菜类').click()
    
    // 选择供应商
    cy.get('.el-select').eq(1).click()
    cy.contains('麦德龙').click()
    
    // 输入数量和价格
    cy.get('input[type="number"]').eq(0).clear().type('5')
    cy.get('input[type="number"]').eq(1).clear().type('10.5')
    
    // 输入备注
    cy.get('textarea').type('测试备注')
    
    // 拦截API请求
    cy.intercept('POST', '/api/stock/in').as('stockIn')
    
    // 提交表单
    cy.get('button').contains('提交').click()
    
    // 等待API请求完成
    cy.wait('@stockIn').then((interception) => {
      // 验证请求体
      expect(interception.request.body).to.include({
        name: '测试食材',
        category: 'vegetable',
        supplier: 'maidelong',
        quantity: 5,
        price: 10.5,
        remark: '测试备注'
      })
      
      // 如果API返回成功
      if (interception.response.statusCode === 201) {
        // 验证成功提示
        cy.contains('入库成功').should('be.visible')
        
        // 验证表单重置
        cy.get('input[placeholder="请输入食材名称"]').should('have.value', '')
      }
    })
  })

  it('应该验证必填字段', () => {
    // 不填写任何内容直接提交
    cy.get('button').contains('提交').click()
    
    // 验证错误提示
    cy.contains('请输入食材名称').should('be.visible')
    cy.contains('请选择分类').should('be.visible')
    cy.contains('请选择供应商').should('be.visible')
  })

  it('应该处理API错误', () => {
    // 填写表单
    cy.get('input[placeholder="请输入食材名称"]').type('测试食材')
    cy.get('.el-select').eq(0).click()
    cy.contains('蔬菜类').click()
    cy.get('.el-select').eq(1).click()
    cy.contains('麦德龙').click()
    cy.get('input[type="number"]').eq(0).clear().type('5')
    
    // 模拟API错误
    cy.intercept('POST', '/api/stock/in', {
      statusCode: 500,
      body: { error: '服务器错误' }
    }).as('stockInError')
    
    // 提交表单
    cy.get('button').contains('提交').click()
    
    // 等待API请求完成
    cy.wait('@stockInError')
    
    // 验证错误提示
    cy.contains('入库失败').should('be.visible')
  })
})