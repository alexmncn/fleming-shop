import { firstValueFrom } from "rxjs";
import { CatalogApiService } from "./catalog-api.service";
import { Injectable, signal } from "@angular/core";

import { Family } from "../../models/family.model";

@Injectable({ providedIn: 'root' })
export class FamilyStore {
  families = signal<Family[]>([]);
  total = signal(0);
  loading = signal(false);
  statusCode = signal(0);

  constructor(private api: CatalogApiService) {}

  async loadTotal() {
    try {
      const res = await firstValueFrom(this.api.getTotalFamilies());
      this.total.set(res.total);
    } catch (err: any) {
      this.statusCode.set(err.status || 500);
    }
  }

  async load() {
    this.loading.set(true);
    try {
      const data = await firstValueFrom(this.api.getFamilies());
      this.families.set(data);
    } catch (err: any) {
      this.statusCode.set(err.status || 500);
    } finally {
      this.loading.set(false);
    }
  }
}