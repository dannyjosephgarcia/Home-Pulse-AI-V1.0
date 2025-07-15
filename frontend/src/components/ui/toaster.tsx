import { Toaster as HotToaster } from 'react-hot-toast';

const Toaster = () => {
  return (
    <HotToaster
      position="top-right"
      toastOptions={{
        // Default options for all toasts
        style: {
          background: '#333',
          color: '#fff',
          fontWeight: 'bold',
          borderRadius: '8px',
        },
        duration: 4000,
        success: {
          style: {
            background: 'green',
          },
        },
        error: {
          style: {
            background: 'red',
          },
        },
      }}
    />
  );
};

export default Toaster;
