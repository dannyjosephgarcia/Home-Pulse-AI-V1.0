import { useCallback } from 'react';

interface ToastOptions {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

export const useToast = () => {
  const toast = useCallback(({ title, description, variant = 'default' }: ToastOptions) => {
    const toastContainer = document.createElement('div');
    toastContainer.className = `
      fixed top-4 right-4 z-50 max-w-sm w-full p-4 rounded-lg shadow-lg transition-all
      ${variant === 'destructive' ? 'bg-red-600 text-white' : 'bg-gray-800 text-white'}
    `;

    toastContainer.innerHTML = `
      <strong class="block text-base font-semibold mb-1">${title}</strong>
      ${description ? `<span class="text-sm">${description}</span>` : ''}
    `;

    document.body.appendChild(toastContainer);

    setTimeout(() => {
      toastContainer.style.opacity = '0';
      toastContainer.style.transform = 'translateX(20px)';
      setTimeout(() => document.body.removeChild(toastContainer), 300);
    }, 3000);
  }, []);

  return { toast };
};
