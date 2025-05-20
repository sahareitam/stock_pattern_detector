export function createPageUrl(pageName) {
  if (pageName === 'Home') return '/';
  return `/${pageName.toLowerCase()}`;
}

// Utility function for merging Tailwind CSS classes
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}