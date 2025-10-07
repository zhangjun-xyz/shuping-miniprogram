//result.js
const app = getApp()

Page({
  data: {
    bookInfo: {},
    doubanInfo: null,
    useAI: false,
    recognitionTypeText: '',
    stars: [],
    showFullIntro: false,
    retryTitle: '',
    isRetrying: false
  },

  onLoad: function(options) {
    if (options.data) {
      try {
        const data = JSON.parse(decodeURIComponent(options.data))
        this.initializeData(data)
      } catch (error) {
        console.error('解析参数失败:', error)
        wx.showToast({
          title: '数据解析失败',
          icon: 'none'
        })
      }
    }
  },

  // 初始化数据
  initializeData: function(data) {
    const bookInfo = data.book_info || {}
    const doubanInfo = data.douban_info || null
    const useAI = data.use_ai || false

    // 设置识别类型文本
    let recognitionTypeText = useAI ? 'AI自动识别' : '手动输入'

    // 计算星级（基于豆瓣评分）
    let stars = []
    if (doubanInfo && doubanInfo.rating) {
      const rating = parseFloat(doubanInfo.rating)
      const fullStars = Math.floor(rating / 2)
      const hasHalfStar = (rating % 2) >= 1

      for (let i = 0; i < 5; i++) {
        if (i < fullStars) {
          stars.push(true)
        } else if (i === fullStars && hasHalfStar) {
          stars.push(true)
        } else {
          stars.push(false)
        }
      }
    }

    this.setData({
      bookInfo: bookInfo,
      doubanInfo: doubanInfo,
      useAI: useAI,
      recognitionTypeText: recognitionTypeText,
      stars: stars,
      retryTitle: bookInfo.title || ''
    })

    console.log('结果页面数据:', {
      bookInfo,
      doubanInfo,
      useAI
    })
  },

  // 返回首页
  goBack: function() {
    wx.navigateBack({
      delta: 1
    })
  },

  // 切换简介显示
  toggleIntro: function() {
    this.setData({
      showFullIntro: !this.data.showFullIntro
    })
  },

  // 打开豆瓣页面
  openDoubanPage: function() {
    if (!this.data.doubanInfo || !this.data.doubanInfo.url) {
      wx.showToast({
        title: '没有豆瓣链接',
        icon: 'none'
      })
      return
    }

    // 复制链接到剪贴板
    wx.setClipboardData({
      data: this.data.doubanInfo.url,
      success: function() {
        wx.showModal({
          title: '提示',
          content: '豆瓣链接已复制到剪贴板，请在浏览器中打开',
          showCancel: false,
          confirmText: '知道了'
        })
      }
    })
  },

  // 重试输入
  onRetryInput: function(e) {
    this.setData({
      retryTitle: e.detail.value
    })
  },

  // 重新搜索
  retrySearch: function() {
    if (!this.data.retryTitle.trim()) {
      wx.showToast({
        title: '请输入书名',
        icon: 'none'
      })
      return
    }

    this.setData({
      isRetrying: true
    })

    const that = this
    app.request({
      url: '/api/search-douban',
      method: 'POST',
      data: {
        title: this.data.retryTitle.trim()
      }
    }).then(function(data) {
      if (data.success && data.data) {
        // 更新豆瓣信息
        that.setData({
          doubanInfo: data.data
        })

        // 重新计算星级
        let stars = []
        if (data.data.rating) {
          const rating = parseFloat(data.data.rating)
          const fullStars = Math.floor(rating / 2)
          const hasHalfStar = (rating % 2) >= 1

          for (let i = 0; i < 5; i++) {
            if (i < fullStars) {
              stars.push(true)
            } else if (i === fullStars && hasHalfStar) {
              stars.push(true)
            } else {
              stars.push(false)
            }
          }
        }

        that.setData({
          stars: stars
        })

        wx.showToast({
          title: '搜索成功',
          icon: 'success'
        })
      } else {
        wx.showToast({
          title: data.error || '未找到相关书籍',
          icon: 'none'
        })
      }
    }).catch(function(error) {
      console.error('重新搜索失败:', error)
      wx.showToast({
        title: '搜索失败，请检查网络',
        icon: 'none'
      })
    }).finally(function() {
      that.setData({
        isRetrying: false
      })
    })
  },

  // 分享结果
  shareResult: function() {
    if (!this.data.doubanInfo) {
      return
    }

    const bookInfo = this.data.bookInfo
    const doubanInfo = this.data.doubanInfo
    const rating = doubanInfo.rating ? `${doubanInfo.rating}/10` : '暂无评分'

    const shareText = `我在书评助手中发现了这本好书：\n\n📖 ${bookInfo.title || doubanInfo.title}\n👤 ${bookInfo.author || doubanInfo.author}\n⭐ 豆瓣评分：${rating}\n\n快来一起看看吧！`

    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })

    // 设置分享内容
    this.onShareAppMessage = function() {
      return {
        title: `发现好书：${bookInfo.title || doubanInfo.title}`,
        path: `/pages/result/result?data=${encodeURIComponent(JSON.stringify({
          book_info: bookInfo,
          douban_info: doubanInfo,
          use_ai: this.data.useAI
        }))}`,
        imageUrl: '' // 可以设置分享图片
      }
    }

    wx.showToast({
      title: '长按右上角分享',
      icon: 'none'
    })
  },

  // 分享给好友
  onShareAppMessage: function() {
    const bookInfo = this.data.bookInfo
    const doubanInfo = this.data.doubanInfo

    return {
      title: `发现好书：${bookInfo.title || doubanInfo.title}`,
      path: `/pages/result/result?data=${encodeURIComponent(JSON.stringify({
        book_info: bookInfo,
        douban_info: doubanInfo,
        use_ai: this.data.useAI
      }))}`,
      imageUrl: ''
    }
  }
})