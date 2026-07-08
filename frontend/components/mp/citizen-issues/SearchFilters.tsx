"use client";

interface SearchFiltersProps {
  search: string;
  category: string;
  ward: string;
  status: string;
  priority: string;
  sort: string;

  categoryOptions: string[];
  wardOptions: string[];
  statusOptions: string[];
  priorityOptions: string[];
  sortOptions: string[];

  onSearchChange: (value: string) => void;
  onCategoryChange: (value: string) => void;
  onWardChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onPriorityChange: (value: string) => void;
  onSortChange: (value: string) => void;
}

interface SelectProps {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}

function SelectField({ label, value, options, onChange }: SelectProps) {
  return (
    <label className="flex flex-col gap-1">
      <span className="pl-1 text-[10px] font-bold uppercase tracking-wider text-[#74777C]">
        {label}
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-2xl border border-[#C3C7CC]/40 bg-[#F7F9FC] px-4 py-3 text-sm font-medium text-black outline-none transition-all focus:border-[#455F87]"
      >
        {options.map((option) => (
          <option key={option}>{option}</option>
        ))}
      </select>
    </label>
  );
}

export default function SearchFilters({
  search,
  category,
  ward,
  status,
  priority,
  sort,

  categoryOptions,
  wardOptions,
  statusOptions,
  priorityOptions,
  sortOptions,

  onSearchChange,
  onCategoryChange,
  onWardChange,
  onStatusChange,
  onPriorityChange,
  onSortChange,
}: SearchFiltersProps) {
  return (
    <div className="glass-card bento-item mb-8 rounded-[24px] p-6">
      {/* Search — full width */}
      <div className="relative mb-4">
        <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#74777C]">
          search
        </span>
        <input
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by issue ID, description or ward…"
          className="w-full rounded-2xl border border-[#C3C7CC]/40 bg-[#F7F9FC] py-3 pl-12 pr-4 text-sm outline-none transition-all focus:border-[#455F87]"
        />
      </div>

      {/* Filters — five equal columns */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
        <SelectField label="Category" value={category} options={categoryOptions} onChange={onCategoryChange} />
        <SelectField label="Ward" value={ward} options={wardOptions} onChange={onWardChange} />
        <SelectField label="Status" value={status} options={statusOptions} onChange={onStatusChange} />
        <SelectField label="Priority" value={priority} options={priorityOptions} onChange={onPriorityChange} />
        <SelectField label="Sort" value={sort} options={sortOptions} onChange={onSortChange} />
      </div>
    </div>
  );
}
