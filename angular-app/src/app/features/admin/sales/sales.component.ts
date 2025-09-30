import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIcon } from '@angular/material/icon';

import { CalendarComponent } from '../../../shared/calendar/calendar.component';

import { Ticket } from '../../../models/ticket.model';
import { TicketItem } from '../../../models/ticketItem.model';

import { SalesService } from '../../../services/admin/data/sales/sales.service';
import { CapitalizePipe } from '../../../pipes/capitalize/capitalize-pipe';
import { CapitalizeFirstPipe } from '../../../pipes/capitalize/capitalize-first-pipe';
import { DailySales } from '../../../models/dailySales.model';


@Component({
  selector: 'app-sales',
  imports: [CommonModule, CalendarComponent, CapitalizePipe, CapitalizeFirstPipe, MatIcon],
  templateUrl: './sales.component.html',
  styleUrl: './sales.component.css'
})
export class SalesComponent implements OnInit{
  dailySalesDates: string[] = [];
  selectedDate: Date | null = null;
  daySales: DailySales[] | null = null;

  tickets: Ticket[] = [];
  selectedTicket: Ticket | null = null;

  ticketItems: TicketItem[] = [];

  constructor(private salesService: SalesService) {}

  ngOnInit(): void {
    this.salesService.getDailySalesDates().subscribe(days => {
      this.dailySalesDates = days;
    });
  }

  onDateSelected(date: Date) {
    this.selectedDate = date;
    const formattedDate = this.formatDateToShortString(date);

    this.selectedTicket = null;
    this.ticketItems = [];
    
    this.salesService.getDaySales(formattedDate).subscribe(daySales => {
      this.daySales = daySales;
    });

    this.salesService.getTicketsByDate(formattedDate).subscribe(tickets => {
      this.tickets = tickets;
    });
  }

  onTicketSelected(ticket: Ticket) {
    this.selectedTicket = ticket;
    this.salesService.getItemsByTicket(ticket.number).subscribe(items => {
      this.ticketItems = items;

      //setTimeout(() => this.scrollToTicketDetails(), 500);
    });
  }

  scrollToTicketDetails() {
    if (window.innerWidth > 600) {
      return; // No hacer scroll si la pantalla es grande
    }

    const el = document.getElementById('ticketDetails');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  }

  formatDateToShortString(date: Date): string {
    return `${String(date.getDate()).padStart(2, '0')}-${String(date.getMonth() + 1).padStart(2, '0')}-${date.getFullYear()}`;
  }

  formatDateToLongString(date: Date): string {
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',   // lunes, martes...
      day: 'numeric',    // 12
      month: 'long',     // diciembre
      year: 'numeric'    // 2025
    }).replace(',', '');
  }
}
