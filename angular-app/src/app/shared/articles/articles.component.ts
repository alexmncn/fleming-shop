import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SelectModule } from 'primeng/select';

import { ArticleComponent } from '../article/article.component';
import { Article } from '../../models/article.model';

@Component({
    selector: 'app-articles',
    imports: [CommonModule, ArticleComponent, FormsModule, SelectModule],
    templateUrl: './articles.component.html',
    styleUrl: './articles.component.css'
})
export class ArticlesComponent {
  @Output() loadArticles = new EventEmitter();
  @Output() sortChanged = new EventEmitter<{ order_by: string, direction: string }>();
  @Input() articles: any[]= [];
  @Input() headerTitle: string = '';
  @Input() totalArticles: number = 0;
  @Input() perPage: number = 20;
  @Input() loadingArticles: boolean = false;
  @Input() statusCode: number = -1;
  @Input() defOrderBy: string = '';
  @Input() defDirection: string = '';
  gridDisplay: boolean = true;
  listDisplay: boolean = false;
  placeholders: Article[] = new Array(this.perPage).fill('');

  sortOptions = [
    { name: 'Nombre: A a Z', order_by: 'detalle', direction: 'asc' },
    { name: 'Nombre: Z a A', order_by: 'detalle', direction: 'desc' },
    { name: 'Precio: de menor a mayor', order_by: 'pvp', direction: 'asc' },
    { name: 'Precio: de mayor a menor', order_by: 'pvp', direction: 'desc' },
    { name: 'Fecha: más reciente', order_by: 'date', direction: 'desc' },
    { name: 'Fecha: más antigua', order_by: 'date', direction: 'asc' }
  ];

  selectedSort = this.sortOptions[0];

  constructor(private router: Router) {}

  ngOnInit(): void {

    this.checkRouteAndModifySortOptions();
  }

  checkRouteAndModifySortOptions() {
    const currentRoute = this.router.url;
    const searchRoute = '/catalog/search';

    // Si estamos en la ruta de busqueda, agregar la opción "Relevancia"
    if (currentRoute.includes(searchRoute)) {
      this.sortOptions.unshift({ name: 'Relevancia', order_by: '', direction: '' });
      this.selectedSort = this.sortOptions[0];
    }

    // Si hay valores por defecto, buscar la opción correspondiente y seleccionarla
    if (this.defOrderBy && this.defDirection) {
      const foundOption = this.sortOptions.find(option => option.order_by === this.defOrderBy && option.direction === this.defDirection);
      if (foundOption) {
        this.selectedSort = foundOption;
      }
    }
  }

  onSortChange(clear: boolean): void {
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
