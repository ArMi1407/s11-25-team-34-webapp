// ErrorMessage.jsx
export const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="text-center py-8">
      <p className="text-red-500 mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Reintentar
        </button>
      )}
    </div>
  );
};
