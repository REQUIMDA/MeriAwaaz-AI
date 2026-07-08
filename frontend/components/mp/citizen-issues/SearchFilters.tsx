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
  value: string;
  options: string[];
  onChange: (value: string) => void;
}

function SelectField({
  value,
  options,
  onChange,
}: SelectProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="
        w-full
        rounded-2xl
        border
        border-[#C3C7CC]/40
        bg-[#F7F9FC]
        px-4
        py-3
        text-sm
        font-medium
        text-black
        outline-none
        transition-all
        focus:border-[#455F87]
      "
    >
      {options.map((option) => (
        <option key={option}>{option}</option>
      ))}
    </select>
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

      <div className="grid grid-cols-1 gap-4 md:grid-cols-12">

        {/* Search */}

        <div className="relative md:col-span-4">

          <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#74777C]">
            search
          </span>

          <input
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by Issue ID or Citizen..."
            className="
              w-full
              rounded-2xl
              border
              border-[#C3C7CC]/40
              bg-[#F7F9FC]
              py-3
              pl-12
              pr-4
              text-sm
              outline-none
              transition-all
              focus:border-[#455F87]
            "
          />

        </div>

        {/* Category */}

        <div className="md:col-span-2">
          <SelectField
            value={category}
            options={categoryOptions}
            onChange={onCategoryChange}
          />
        </div>

        {/* Ward */}

        <div className="md:col-span-2">
          <SelectField
            value={ward}
            options={wardOptions}
            onChange={onWardChange}
          />
        </div>

        {/* Status */}

        <div className="md:col-span-2">
          <SelectField
            value={status}
            options={statusOptions}
            onChange={onStatusChange}
          />
        </div>

        {/* Priority */}

        <div className="md:col-span-1">
          <SelectField
            value={priority}
            options={priorityOptions}
            onChange={onPriorityChange}
          />
        </div>

        {/* Sort */}

        <div className="md:col-span-1">
          <SelectField
            value={sort}
            options={sortOptions}
            onChange={onSortChange}
          />
        </div>

      </div>

    </div>
  );
}