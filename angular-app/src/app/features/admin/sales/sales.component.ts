import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CalendarComponent } from '../../../shared/calendar/calendar.component';

import { Ticket } from '../../../models/ticket.model';
import { TicketItem } from '../../../models/ticketItem.model';

import { SalesService } from '../../../services/admin/data/sales/sales.service';


@Component({
  selector: 'app-sales',
  imports: [CommonModule, CalendarComponent],
  templateUrl: './sales.component.html',
  styleUrl: './sales.component.css'
})
export class SalesComponent implements OnInit{
  dailySalesDates: string[] = [];
  selectedDate: string | null = null;

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
    
    this.salesService.getTicketsByDate(date).subscribe(tickets => {
      this.tickets = tickets;
    });
  }

  onTicketSelected(ticket: Ticket) {
    this.selectedTicket = ticket;
    this.salesService.getItemsByTicket(ticket.number).subscribe(items => {
      this.ticketItems = items;
    });
  }
}
