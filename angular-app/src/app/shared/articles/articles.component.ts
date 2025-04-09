import { Component, EventEmitter, Input, Output, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DropdownModule } from 'primeng/dropdown';
import { SelectModule } from 'primeng/select';

import { ArticleComponent } from '../article/article.component';
import { Article } from '../../models/article.model';

interface SortByOption {
  name: string;
  code: number;
}

@Component({
    selector: 'app-articles',
    imports: [CommonModule, ArticleComponent, FormsModule, DropdownModule, SelectModule],
    templateUrl: './articles.component.html',
    styleUrl: './articles.component.css'
})
export class ArticlesComponent {
  @Output() loadArticles = new EventEmitter();
  @Output() sortChanged = new EventEmitter<{ order_by: string, direction: string }>();
  @Input() articles: any[]= [];
  @Input() headerTitle: string = '';
  @Input() totalArticles: number = 0;
  @Input() per_page: number = 20;
  @Input() loadingArticles: boolean = false;
  @Input() statusCode: number = -1;
  gridDisplay: boolean = true;
  listDisplay: boolean = false;
  placeholders: Article[] = new Array(this.per_page).fill('');

  sortOptions = [
    { name: 'Nombre: A a Z', order_by: 'detalle', direction: 'asc' },
    { name: 'Nombre: Z a A', order_by: 'detalle', direction: 'desc' },
    { name: 'Precio: de menor a mayor', order_by: 'pvp', direction: 'asc' },
    { name: 'Precio: de mayor a menor', order_by: 'pvp', direction: 'desc' },
  ];

  selectedSort = this.sortOptions[0];

  onSortChange(): void {
    this.sortChanged.emit({
      order_by: this.selectedSort.order_by,
      direction: this.selectedSort.direction
    });
  }

  load(): void {
    this.loadArticles.emit();
  }

  get allArticlesLoaded(): boolean {
    return this.articles.length === this.totalArticles;
  }

  setGridDisplay(): void {
    if (this.gridDisplay == false) {
      this.gridDisplay = true;
      this.listDisplay = false;
    }
  }

  setListDisplay(): void {
    if (this.listDisplay == false) {
      this.listDisplay = true;
      this.gridDisplay = false;
    }
  }

  get noArticles(): boolean {
    return this.statusCode == 404 && this.articles.length == 0 && !this.loadingArticles;
  }

  get serverError(): boolean {
    return (this.statusCode == 408 || this.statusCode.toString().startsWith('5')) && this.articles.length == 0 && !this.loadingArticles;
  }

}
