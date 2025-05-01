import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-calendar',
  imports: [CommonModule],
  templateUrl: './calendar.component.html',
  styleUrls: ['./calendar.component.css']
})
export class CalendarComponent implements OnInit {
  @Input() markedDates: string[] = [];
  @Output() dateSelected = new EventEmitter<string>();

  currentDate = new Date();
  currentMonthDays: Date[] = [];

  selectedDate: Date | null = null;

  ngOnInit(): void {
    this.generateCalendar();
  }

  isMarked(date: Date): boolean {
    const dateString = `${String(date.getDate()).padStart(2, '0')}-${String(date.getMonth() + 1).padStart(2, '0')}-${date.getFullYear()}`;
    return this.markedDates.includes(dateString);
  }

  isSelected(date: Date): boolean {
    return this.selectedDate?.getTime() === date.getTime();
  }

  generateCalendar() {
    const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
    const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);

    const days: Date[] = [];

    // Llenar días del mes anterior para alinear
    const startDay = firstDay.getDay(); // 0 = domingo
    for (let i = startDay - 1; i >= 0; i--) {
      const d = new Date(firstDay);
      d.setDate(d.getDate() - i - 1);
      days.push(d);
    }

    // Días del mes actual
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push(new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), i));
    }

    this.currentMonthDays = days;
  }

  changeMonth(offset: number) {
    this.currentDate.setMonth(this.currentDate.getMonth() + offset);
    this.generateCalendar();
  }

  selectDate(date: Date) {
    const formatted = `${String(date.getDate()).padStart(2, '0')}-${String(date.getMonth() + 1).padStart(2, '0')}-${date.getFullYear()}`;

    if (this.isMarked(date)) {
      this.selectedDate = date;
      this.dateSelected.emit(formatted);
    }
  }

  getMonthName(): string {
    return this.currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
  }
}

