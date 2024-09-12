import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'capitalize',
  standalone: true
})
export class CapitalizePipe implements PipeTransform {

  transform(value: string): string {
    if (!value) return value

    return value.toLowerCase().replace(/(?:^|\s)([a-zA-Záéíóúñ])/g, (_, first) => ` ${first.toUpperCase()}`).trim();
  }

}
