import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIcon } from '@angular/material/icon';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize.pipe';

@Component({
  selector: 'app-calendar',
  imports: [CommonModule, MatIcon, CapitalizePipe],
  templateUrl: './calendar.component.html',
  styleUrls: ['./calendar.component.css']
})
export class CalendarComponent implements OnInit {
  @Input() markedDates: string[] = [];
  @Output() dateSelected = new EventEmitter<string>();

  daysOfWeek: string[] = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

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

    // Ajustar índice: que lunes = 0, martes = 1, ..., domingo = 6
    let startDay = firstDay.getDay(); // JS: domingo = 0
    startDay = (startDay + 6) % 7;    // ahora lunes = 0, martes = 1, ..., domingo = 6

    // Llenar días del mes anterior para alinear
    for (let i = startDay - 1; i >= 0; i--) {
      const d = new Date(firstDay);
      d.setDate(d.getDate() - i - 1);
      days.push(d);
    }

    // Días del mes actual
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push(new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), i));
    }

    // Rellenar con días del mes siguiente
    let endDay = lastDay.getDay();
    endDay = (endDay + 6) % 7; // ajustar formato lunes=0
    const remaining = 6 - endDay; // días que faltan para completar la semana

    for (let i = 1; i <= remaining; i++) {
      const d = new Date(lastDay);
      d.setDate(d.getDate() + i);
      days.push(d);
    }

    this.currentMonthDays = days;
  }

  changeMonth(offset: number) {
    this.currentDate.setMonth(this.currentDate.getMonth() + offset);
    this.generateCalendar();
  }

  selectDate(date: Date) {
    const formatted = `${String(date.getDate()).padStart(2, '0')}-${String(date.getMonth() + 1).padStart(2, '0')}-${date.getFullYear()}`;

    const currentYear = this.currentDate.getFullYear();
    const currentMonth = this.currentDate.getMonth();

    const clickedYear = date.getFullYear();
    const clickedMonth = date.getMonth();

    // Calcular offset en meses entre las dos fechas
    const offset = (clickedYear - currentYear) * 12 + (clickedMonth - currentMonth);

    if (offset !== 0) {
      this.changeMonth(offset);
    }

    this.selectedDate = date;
    this.dateSelected.emit(formatted);
  }

  getMonthName(): string {
    return this.currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
  }

  isToday(date: Date): boolean {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
  }
}

