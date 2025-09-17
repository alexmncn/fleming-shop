import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CalendarComponent } from '../../../shared/calendar/calendar.component';

import { Ticket } from '../../../models/ticket.model';
import { TicketItem } from '../../../models/ticketItem.model';

import { SalesService } from '../../../services/admin/data/sales/sales.service';
import { CapitalizePipe } from "../../../pipes/capitalize/capitalize.pipe";
import { DailySales } from '../../../models/dailySales.model';


@Component({
  selector: 'app-sales',
  imports: [CommonModule, CalendarComponent, CapitalizePipe],
  templateUrl: './sales.component.html',
  styleUrl: './sales.component.css'
})
export class SalesComponent implements OnInit{
  dailySalesDates: string[] = [];
  selectedDate: string | null = null;
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

  onDateSelected(date: string) {
    this.selectedDate = date;
    this.selectedTicket = null;
    this.ticketItems = [];
    
    this.salesService.getDaySales(date).subscribe(daySales => {
      this.daySales = daySales;
    });

    this.salesService.getTicketsByDate(date).subscribe(tickets => {
      this.tickets = tickets;
    });
  }

  onTicketSelected(ticket: Ticket) {
    this.selectedTicket = ticket;
    this.salesService.getItemsByTicket(ticket.number).subscribe(items => {
      this.ticketItems = items;

      setTimeout(() => this.scrollToTicketDetails(), 500);
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
}
