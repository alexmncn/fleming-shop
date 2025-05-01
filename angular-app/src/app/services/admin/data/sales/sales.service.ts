import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';

import { Ticket } from '../../../../models/ticket.model';
import { TicketItem } from '../../../../models/ticketItem.model';
import { DailySales } from '../../../../models/dailySales.model';

@Injectable({
  providedIn: 'root'
})
export class SalesService {
  private baseUrl = environment.apiUrl;
  private dailySalesDatesUrl: string = this.baseUrl + '/sales/daily_sales/dates';
  private daySalesUrl: string = this.baseUrl + '/sales/day_sales';
  private daySalesTicketsUrl: string = this.baseUrl + '/sales/day_sales/tickets';
  private ticketItemsUrl: string = this.baseUrl + '/sales/day_sales/ticket/items';

  constructor(private http: HttpClient) {}

  getDailySalesDates() {
    return this.http.get<string[]>(this.dailySalesDatesUrl);
  }

  getDaySales(date: string) {
    return this.http.get<DailySales[]>(this.daySalesUrl, { params: { date } });
  }

  getTicketsByDate(date: string) {
    return this.http.get<Ticket[]>(this.daySalesTicketsUrl, { params: { date } });
  }

  getItemsByTicket(ticketNumber: number) {
    return this.http.get<TicketItem[]>(this.ticketItemsUrl, { params: { ticket_number: ticketNumber.toString() } });
  }
}
