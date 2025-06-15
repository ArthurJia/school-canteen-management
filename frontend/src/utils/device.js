export function isMobile() {
  // 检查用户代理
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i;
  
  // 检查屏幕宽度
  const isSmallScreen = window.innerWidth < 768;
  
  return mobileRegex.test(userAgent) || isSmallScreen;
}