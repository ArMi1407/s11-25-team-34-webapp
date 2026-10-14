import { Search } from 'lucide-react';

export const SearchBar = () => {
  return (
    <div
      className="flex items-center w-full h-12 gap-2 p-4 rounded-3xl bg-primary border-primary 
                   sm:w-lg xl:h-8 xl:rounded-2xl"
    >
      <Search size={24} className="text-text-secondary shrink-0" />
      <input
        placeholder="Search..."
        className="w-full bg-transparent border-none outline-none text-text-secondary text-sm"
      />
    </div>
  );
};
