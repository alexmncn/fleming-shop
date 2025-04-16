import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, NavigationExtras } from '@angular/router';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';

import { environment } from '../../../environments/environment';
import { ArticlesService } from '../../services/catalog/articles/articles.service';
import { MessageService } from '../../services/message/message.service';

@Component({
    selector: 'app-search-bar',
    imports: [FormsModule, IconFieldModule, InputIconModule, InputTextModule],
    templateUrl: './search-bar.component.html',
    styleUrl: './search-bar.component.css'
})
export class SearchBarComponent implements OnInit {
  @Output() isFocused = new EventEmitter<boolean>();
  searchParam: string = '';
  isInputFocused: boolean = false;

  totalArticles: any = 'todos los'; 

  constructor(private articlesService: ArticlesService, private messageService: MessageService, private router: Router) { }

  ngOnInit(): void {
    this.loadTotalArticles();
  }

  loadTotalArticles(): void {
    this.articlesService.getTotalArticles().subscribe({
      next: (res) => this.totalArticles = res.total,
      error: (err) => {
        console.error('Error fetching total:', err);
      }
    });
  }

  get placeholder(): string {
    return 'Buscar entre ' + this.totalArticles + ' artículos';
  }

  onSearch(): void {
    this.onBlur();
    if (this.searchParam !== '') {
      const navigationExtras: NavigationExtras = {
        queryParams: { 'q': this.searchParam }
      };

      this.router.navigate(['/catalog/search'], navigationExtras);;
    } else {
      this.messageService.showMessage('info', 'Introduce un término de búsqueda', 5);
    }
  }

  onFocus(): void {
    this.isInputFocused = true;
    this.isFocused.emit(this.isInputFocused);
  }

  onBlur(): void {
    this.isInputFocused = false;
    this.isFocused.emit(this.isInputFocused);
  }
}
