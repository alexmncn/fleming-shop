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
  @Input() articles: any[]= [];
  @Input() headerTitle: string = '';
  @Input() totalArticles: number = 0;
  @Input() per_page: number = 20;
  @Input() loadingArticles: boolean = false;
  @Input() statusCode: number = -1;
  gridDisplay: boolean = true;
  listDisplay: boolean = false;
  placeholders: Article[] = new Array(this.per_page).fill('');

  sortOptions: SortByOption[] = [
    { name: 'Precio: de menor a mayor', code: 0 },
    { name: 'Precio: de mayor a menor', code: 1 },
    { name: 'Nombre: A a Z', code: 2 },
    { name: 'Nombre: Z a A', code: 3 }
  ];

  selectedSort: SortByOption | undefined;

  ngOnChanges(changes: SimpleChanges): void {
    if(changes["loadingArticles"])


    if (changes["articles"]) {
      this.sortArticles();
    }
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

  sortArticles() {
    switch (this.selectedSort?.code) {
      case 0:
        this.articles.sort((a, b) => a.pvp - b.pvp);
        break;
      case 1:
        this.articles.sort((a, b) => b.pvp - a.pvp);
        break; 
      case 2:
        this.articles.sort((a, b) => a.detalle.localeCompare(b.detalle));
        break;
      case 3:
        this.articles.sort((a, b) => b.detalle.localeCompare(a.detalle));
        break;
      default:
        break;
    }
  }

  get noArticles(): boolean {
    return this.statusCode == 404 && this.articles.length == 0 && !this.loadingArticles;
  }

  get serverError(): boolean {
    return (this.statusCode == 408 || this.statusCode.toString().startsWith('5')) && this.articles.length == 0 && !this.loadingArticles;
  }

}
