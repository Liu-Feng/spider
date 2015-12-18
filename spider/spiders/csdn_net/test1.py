package com.ufida.report.anareport.expand;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import nc.pub.smart.metadata.Field;

import com.ufida.report.anareport.IFldCountType;
import com.ufida.report.anareport.data.AbsRowData;
import com.ufida.report.anareport.data.DetailRowData;
import com.ufida.report.anareport.data.GroupDataSet;
import com.ufida.report.anareport.data.GroupRowData;
import com.ufida.report.anareport.data.MemoryRowData;
import com.ufida.report.anareport.data.RowDataArray;
import com.ufida.report.anareport.data.RowDataComparator;
import com.ufida.report.anareport.model.AnaDataSetTool;
import com.ufida.report.anareport.model.AnaRepField;
import com.ufida.report.anareport.model.AreaDataModel;
import com.ufida.report.anareport.model.ElseField;
import com.ufida.report.anareport.model.FieldCountDef;
import com.ufida.report.anareport.model.TopNSetInfo;
import com.ufida.report.anareport.util.FreeFieldConverter;
import com.ufida.report.anareport.util.SortArrayUtil;

public class ListTopNProcessor extends AbsGroupDataProcessor {
	private ArrayList<Integer> al_procLvl = null;

	public ListTopNProcessor(AreaDataModel areaModel) {
		super(areaModel);
		al_procLvl = new ArrayList<Integer>();
	}

	@Override
	protected boolean isEnabledProc(AnaRepField fld) {
		TopNSetInfo topN = (TopNSetInfo) fld.getTopNInfo();
		if (topN != null && topN.isEnabled()) {
			FieldCountDef def = fld.getFieldCountDef();
			if (def != null && !def.hasRangeField())// ��������Χ�ġ��ϼơ����޷�����TopN
				return false;
			int procLvl = getProcLvl(fld);
			if (al_procLvl.contains(procLvl)) {// ͬһ��������ֻ����һ����Ч
				topN.setEnabled(false);
				return false;
			} else {
				al_procLvl.add(procLvl);
				return true;
			}
		}
		return false;
	}

	@Override
	protected ProcRowDatas processRowDatas(GroupDataSet grpDataSet, AbsRowData parentRow, RowDataArray rowData,
			AnaRepField fld, int[] lvlCount, int plvl, String col) {
		TopNSetInfo topN = (TopNSetInfo) fld.getTopNInfo();

		// ��������		
		RowDataComparator comp = new RowDataComparator(grpDataSet, col, topN.isASC());
		List<AbsRowData> sortedRows = new ArrayList<AbsRowData>();
		if(rowData == null){
			return null ;
		}
		int len = rowData.length();
		for(int i = 0;i<len;i++){
			sortedRows.add(rowData.get(i));
		}
		SortArrayUtil.sortList(sortedRows, comp);
		
		//int[] idx = SortArrayUtil.sortArrayData(rowData, new RowDataComparator(grpDataSet, col, topN.isASC()));
		int idxLen = (sortedRows == null) ? 0 : sortedRows.size();//(idx == null) ? 0 : idx.length;
		int datalen = topN.isExtendN() ? topN.getN() : Math.min(topN.getN(), idxLen);// ��������������
		datalen = Math.max(0, datalen);// ȷ�����Ǹ���

		int retLen = (topN.isShowElse() && (datalen < idxLen || topN.isExtendN())) ? datalen + 1 : datalen;// �����������ݻ���Ҫǿ��ռλʱ����Ҫ����һ��
		// ���÷���������
		RowDataArray rows = new RowDataArray(retLen);
		for (int i = 0; i < datalen; i++) {
			AbsRowData data = null;
			if (i < idxLen)
				data = sortedRows.get(i);
			else
				data = createNullRow(grpDataSet, idxLen == 0 ? parentRow : rowData.get(0), plvl - 1);
			rows.setRowData(i, data);
		}
		// ��������
		if (retLen > datalen) {
			AbsRowData data = null;
			if (idxLen > datalen)
				data = getElseRow(grpDataSet, parentRow, rowData, sortedRows, datalen, fld);
			else
				data = createNullElseRow(grpDataSet, idxLen == 0 ? parentRow : rowData.get(0), fld);
			rows.setRowData(datalen, data);
		}
		RowDataArray rmvRows = null;
		if (datalen < idxLen) {// ��������������
			rmvRows = new RowDataArray(idxLen - datalen);
			for (int i = datalen; i < idxLen; i++) {
				rmvRows.setRowData(i - datalen, sortedRows.get(i));
			}
		}

		ProcRowDatas result = new ProcRowDatas(rows, rmvRows);
		return result;
	}

	/**
	 * edit by guogang 2009-3-3 ֧��TopN�����ֶεĸ�������,�����ӵĴ���???
	 * 
	 * @i18n miufo00335=����
	 */
	private AbsRowData getElseRow(GroupDataSet grpDataSet, AbsRowData parentRow, RowDataArray rowData,List<AbsRowData> sortedRows,
			int begin, AnaRepField fld) {
		AbsRowData first = rowData.get(0);
		TopNSetInfo topN = (TopNSetInfo) fld.getTopNInfo();

		if (first.isDetailData()) {// ��ϸ���ݵġ�������
			DetailRowData row = (DetailRowData) first;
			ArrayList<FieldCountDef> al_aggr = new ArrayList<FieldCountDef>();// ָ���ֶε�ͳ������
			ArrayList<Integer> al_idx = new ArrayList<Integer>(); // ָ���ֶε����
			MemoryRowData data = new MemoryRowData(row.getMetaData(), null);
			Field[] flds = row.getMetaData().getFields();
			ElseField elseField = null;
//			List<ElseField> elseFields = topN.getElseFields() ;
//			FreeFieldConverter converter = m_areaModel.getAreaFields(false).getFieldConverter() ;
//			//��Ϊ��TopNInfo��ѭ������
//			for (int i = 0; i < elseFields.size(); i++) {
//				ElseField elseField = elseFields.get(i) ;
//				String fieldName = converter.getConvertName(elseField.getFieldName()) ;
//				if(fieldName != null){
//					for (int j = 0; j < flds.length; j++) {
//						if(fieldName.equalsIgnoreCase(flds[j].getFldname())){
//							if(!elseField.isCount() && elseField.getShowName() != null){
//								data.setData(j, elseField.getShowName());
//							}else if(elseField.isCount()){
//								al_aggr.add(new FieldCountDef(flds[j], elseField.getCountType()));
//								al_idx.add(j);
//							}
//						}
//					}
//				}
//			}
			for (int i = 0; i < flds.length; i++) {
				elseField = getElseField(topN,flds[i].getFldname());
				if (elseField != null && !elseField.isCount() && elseField.getShowName() != null) {
					data.setData(i, elseField.getShowName());
				} else {

					// if (DataTypeConstant.isNumberType(flds[i].getDataType()))
					// if (flds[i].getExtType() != RptProvider.DIMENSION) {
					if (elseField != null && elseField.isCount()) {
						al_aggr.add(new FieldCountDef(flds[i], elseField.getCountType()));
						al_idx.add(i);
					} else {
						//û��Ļ��������Զ����ӣ���ȫ����topN���öԻ����е����������� zhongkm
						/*if (DataTypeConstant.isNumberType(flds[i].getDataType())) {
							al_aggr.add(new FieldCountDef(flds[i], IFldCountType.TYPE_SUM));// ָ��Ĭ��ͳ�Ʒ�ʽ��sum������Ӧ�ô����û�������
							al_idx.add(i);
						}*/
					}
					// }
				}
			}
			if (al_idx.size() > 0) {
				//����Ψһ�����Ĵ���
				Map<Integer, Set> coutDistinctMap = new HashMap<Integer, Set>();
				for (int i = begin; i < sortedRows.size(); i++) {
					row = (DetailRowData) sortedRows.get(i);//(DetailRowData) rowData.get(idx[i]);
					for (int j = 0; j < al_idx.size(); j++) {
						int m = al_idx.get(j);
						String fName = al_aggr.get(j).getMainFldName();
						Object rowValue = null;
						if (al_aggr.get(j).getCountType() == IFldCountType.TYPE_COUNT)
							rowValue = 1;
						else if (al_aggr.get(j).getCountType() == IFldCountType.TYPE_COUNT_DISTINCT) {// Ψһ����
							Object o = row.getData(fName);
							Set set = coutDistinctMap.get(j);
							if (set == null)
								set = new TreeSet();
							if (o != null && set.add(o)) {
								coutDistinctMap.put(j, set);
								rowValue = 1;
							} else
								rowValue = 0;
						} else
							rowValue = row.getData(fName);

						Object value = AnaDataSetTool.calcValue(data.getData(m), rowValue, al_aggr.get(j)
								.getCountType());
						data.setData(m, value);
					}					
				}
				coutDistinctMap.clear();
				int count = sortedRows.size() - begin;//idx.length - begin;
				for (int j = 0; j < al_idx.size(); j++) {// ����ƽ���������г���
					int m = al_idx.get(j);
					Object dataValue = null;
					if (al_aggr.get(j).getCountType() == IFldCountType.TYPE_AVAGE) {
						dataValue = data.getData(m);
						if (dataValue != null)
							data.setData(m, (Double.parseDouble(dataValue.toString()) / count));
					}
				}
			}
			data.setGroupDatas(first.getGroupDatas());
			return data;
		} else {// �������ݵġ�������
			GroupRowData row = new GroupRowData(grpDataSet, (GroupRowData) first,
					((GroupRowData) first).getGrpLvl() - 1);
			FieldCountDef count = fld.getFieldCountDef();
			FreeFieldConverter converter = m_areaModel.getAreaFields(false).getFieldConverter() ;
			if (count != null) {
				String grpFld = count.getRangeFldName();
				ElseField elseField = topN.getElseField(grpFld);
				if (elseField != null && !elseField.isCount() && elseField.getShowName() != null) {
					grpDataSet.setData(row, converter.getConvertName(grpFld), elseField.getShowName());
				}
			}else if(fld.getField() != null){
				String grpFld = fld.getField().getExpression();
				ElseField elseField = topN.getElseField(grpFld);
				if (elseField != null && !elseField.isCount() && elseField.getShowName() != null) {
					grpDataSet.setData(row, converter.getConvertName(grpFld), elseField.getShowName());
				}
			}
			for (int i = begin; i < sortedRows.size(); i++) {
				row = m_areaModel.getDSTool().appendAggrData(grpDataSet, (GroupRowData) row, sortedRows.get(i),false);//rowData.get(idx[i]), false);
			}
			return row;
		}
	}

	private AbsRowData createNullElseRow(GroupDataSet grpDataSet, AbsRowData row, AnaRepField fld) {
		if(row == null)
			return createNullRow(grpDataSet, row, 1);

		TopNSetInfo topN = (TopNSetInfo) fld.getTopNInfo();
		if (row.isDetailData()) {// ��ϸ���ݵġ�������
			MemoryRowData data = new MemoryRowData(row.getMetaData(), null);
			Field[] flds = row.getMetaData().getFields();
			ElseField elseField = null;
			for (int i = 0; i < flds.length; i++) {
				elseField = getElseField(topN,flds[i].getFldname());
				if (elseField != null && !elseField.isCount() && elseField.getShowName() != null) {
					data.setData(i, elseField.getShowName());
				}
			}
			return data;
		} else {// �������ݵġ�������
			GroupRowData data = new GroupRowData(grpDataSet, (GroupRowData) row,
					((GroupRowData) row).getGrpLvl() - 1);
			FieldCountDef count = fld.getFieldCountDef();
			if (count != null) {
				String grpFld = count.getRangeFldName();
				ElseField elseField = topN.getElseField(grpFld);
				FreeFieldConverter converter = m_areaModel.getAreaFields(false).getFieldConverter() ;
				if (elseField != null && !elseField.isCount() && elseField.getShowName() != null) {
					grpDataSet.setData(data, converter.getConvertName(grpFld), elseField.getShowName());
				}
			}
			return data;
		}
	}
	//ͨ����������
	private ElseField getElseField(TopNSetInfo topN,String fldName){
		List<ElseField> elseFields = topN.getElseFields() ;
		FreeFieldConverter converter = m_areaModel.getAreaFields(false).getFieldConverter() ;
		for (int i = 0; i < elseFields.size(); i++) {
			ElseField elseField = elseFields.get(i) ;
			String fieldName = converter.getConvertName(elseField.getFieldName()) ;
			if(fieldName != null && fieldName.equalsIgnoreCase(fldName)){
				return elseField ;
			}
		}
		return null ;
	}
}
